from hub import port, motion_sensor
import motor
import motor_pair
import runloop

leftMotor = port.C
rightMotor = port.F
leftAttachment = port.B
rightAttachment = port.D

#█████████████████ DON'T TOUCH █████████████████████
motorPair = (motor_pair.PAIR_1,leftMotor,rightMotor)
attachments = (rightAttachment,leftAttachment)
left = 1#███████████████████████████████████████████
right = -1#█████████████████████████████████████████
pair = motor_pair.PAIR_1#███████████████████████████
motion_sensor.reset_yaw(0)#█████████████████████████
motor_pair.pair(*motorPair)#████████████████████████
correctionDivisor = 2#██████████████████████████████
#███████████████████████████████████████████████████

# speed is an integer with the unit degrees/second, angle is a decimal with the unit degrees, direction is the left or right constant, relative is a boolean that resets the gyro for a relative turn
async def turn(speed: int,angle: float,direction: int, relative: bool = False):
    if relative:
        motion_sensor.reset_yaw(0)
    motor_pair.move_tank(motorPair[0],-speed*direction,speed*direction)
    if direction > 0:
        while motion_sensor.tilt_angles()[0] < angle*10:
            await runloop.sleep_ms(1)
    else:
        while motion_sensor.tilt_angles()[0] > -angle*10:
            await runloop.sleep_ms(1)
    motor_pair.stop(motorPair[0])

# speed is an integer with the unit degrees/second, degrees is an integer, smart is a boolean that enables gyro
async def straight(speed: int,degrees: int,smart: bool = False):
    if smart:
        angle = motion_sensor.tilt_angles()[0]
        start = (motor.relative_position(motorPair[2])-motor.relative_position(motorPair[1]))/2
        while (motor.relative_position(motorPair[2])-motor.relative_position(motorPair[1]))/2-start < degrees:
            error = (angle-motion_sensor.tilt_angles()[0])//correctionDivisor
            motor.run_for_degrees(motorPair[1],degrees,-speed+error)
            motor.run_for_degrees(motorPair[2],degrees,speed+error)
        motor.stop(motorPair[1])
        motor.stop(motorPair[2])
    else:
        motor.run_for_degrees(motorPair[1],degrees,-speed)
        await motor.run_for_degrees(motorPair[2],degrees,speed)

# speed is an integer with the unit degrees/second degrees is an integer, side is the left or right constant
async def attachment(speed: int,degrees: int,side: int):
    await motor.run_for_degrees(attachments[int(side/2+0.5)],degrees,speed)

async def main():
    await straight(300,570,smart=True)
    await attachment(-300,170,left)
    await straight(400,700,smart=True)
    await runloop.sleep_ms(200)
runloop.run(main())
