import time
from dotenv import dotenv_values
import RPi.GPIO as GPIO
import servo

# Init needed variables and get config from env file
# Remember to insert correct values to carconfig.env, including correct GPIO mode
config = dotenv_values("carconfig.env")
gpio_mode = config["GPIO_MODE"]
ultrasonic_trigger = config["ULTRASONIC_TRIGGER_PIN"]
ultrasonic_echo = config["ULTRASONIC_ECHO_PIN"]
ultrasonic_servo_channel = config["ULTRASONIC_SERVO_CHANNEL"]
ultrasonic_servo = servo.Servo(ultrasonic_servo_channel)
ultrasonic_servo.setup()

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
    ultrasonic_servo.write(180)
    right_distance = distance()
    ultrasonic_servo.write(90)
    return right_distance

def distance_to_left():
    ultrasonic_servo.write(0)
    left_distance = distance()
    ultrasonic_servo.write(90)
    return left_distance