import sys
import signal
import time
from dotenv import dotenv_values
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import ultrasonic
import temperature

class Driver:
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit)

        # Configuration from env file
        # When running the program remotely, change carconfig to full file path
        self.config = dotenv_values("carconfig.env")
        self.gpio_mode = self.config["GPIO_MODE"]
        self.left_motor = int(self.config["LEFT_MOTOR_PIN"])
        self.right_motor = int(self.config["RIGHT_MOTOR_PIN"])
        self.steer_servo_channel = self.config["RIGHT_MOTOR_PIN"]
        self.kit = ServoKit(channels=16)
        self.steer_servo = self.kit.servo[int(self.steer_servo_channel)]
        self.steer_servo.angle = 90
        
    def exit(self, signum, frame):  
        self.shutdown = True

    # Car control methods
    def drive(self):
        GPIO.output(self.right_motor, GPIO.HIGH)
        GPIO.output(self.left_motor, GPIO.HIGH)

    def stop(self):
        GPIO.output(self.right_motor, GPIO.LOW)
        GPIO.output(self.left_motor, GPIO.LOW)

    def turn_around(self):
        self.steer_servo.angle = 180
        time.sleep(0.5)
        self.steer_servo.angle = 90

    def turn_left(self):
        self.steer_servo.angle = 0
        time.sleep(0.1)
        self.steer_servo.angle = 90

    def turn_right(self):
        self.steer_servo.angle = 180
        time.sleep(0.1)
        self.steer_servo.angle = 90

    # Cleanup before exiting program
    def stop_program(self):
        GPIO.cleanup()

if __name__ == "__main__":
    driver = Driver()
 
    # Runs if no errors occured. If CPU temp exceeds 75, stops the program.
    while not driver.shutdown:
        if (temperature.get_temperature() > 75):
            driver.stop_program()
            sys.exit(0)       
        try: 
            if (ultrasonic.distance() > 30):
                driver.drive()
            else:
                driver.stop()
                if (ultrasonic.distance_to_left() < ultrasonic.distance_to_right()):
                    driver.turn_right()
                    driver.drive()
                elif (ultrasonic.distance_to_left() > ultrasonic.distance_to_right()):
                    driver.turn_left()
                    driver.drive()
                elif ((ultrasonic.distance_to_left < 30) and (ultrasonic.distance_to_right < 30)):
                    driver.turn_around()
                    driver.drive()
        except Exception as error:
            print("Error in driving {}".format(error))
 
    driver.stop_program()
    sys.exit(0)
