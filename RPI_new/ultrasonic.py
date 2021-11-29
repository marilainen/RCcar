import time
from dotenv import dotenv_values
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# Configuration from env file
# When running the program remotely, change carconfig to full file path
config = dotenv_values("carconfig.env")
gpio_mode = config["GPIO_MODE"]
ultrasonic_trigger = int(config["ULTRASONIC_TRIGGER_PIN"])
ultrasonic_echo = int(config["ULTRASONIC_ECHO_PIN"])
ultrasonic_servo_channel = config["ULTRASONIC_SERVO_CHANNEL"]
kit = ServoKit(channels=16)
ultrasonic_servo = kit.servo[int(ultrasonic_servo_channel)]
ultrasonic_servo.angle = 90

GPIO.setmode(gpio_mode)
GPIO.setup(ultrasonic_trigger, GPIO.OUT)
GPIO.setup(ultrasonic_echo, GPIO.IN)

def distance():
    try:
        GPIO.output(ultrasonic_trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(ultrasonic_trigger, GPIO.LOW)
    
        start_time = time.time()
        stop_time = time.time()
    
        while GPIO.input(ultrasonic_echo) == 0:
            start_time = time.time()
    
        while GPIO.input(ultrasonic_echo) == 1:
            stop_time = time.time()
    
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2
        return distance
    except Exception as error:
        print("Error getting data from ultrasonic sensor {}".format(error))

def distance_to_right():
    ultrasonic_servo.angle = 180
    right_distance = distance()
    ultrasonic_servo.angle = 90
    return right_distance

def distance_to_left():
    ultrasonic_servo.angle = 0
    left_distance = distance()
    ultrasonic_servo.angle = 90
    return left_distance
