import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
enable_pin = 18

# Order in datasheet: orange, yellow, pink, blue, red (always 0)
# https://components101.com/motors/28byj-48-stepper-motor
coil_A_1_pin = 17 # orange
coil_A_2_pin = 24 # yellow
coil_B_1_pin = 4 # pink
coil_B_2_pin = 23 # blue

motor_step_angle=5.625 # degrees per step
motor_gear_ratio=64 # 64:1
motor_steps_per_rev = 360/motor_step_angle * motor_gear_ratio;

external_gear_ratio = 10.0/43.0 # motor drives 10 tooth gear, driving 43 tooth gear
external_steps_per_rev = motor_steps_per_rev / external_gear_ratio;
seconds_per_step = 60.0 / external_steps_per_rev;

# adjust if different
Seq = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1],
]
StepCount = len(Seq)

GPIO.setup(enable_pin, GPIO.OUT)

GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

GPIO.output(enable_pin, 1)

def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

def forward(seconds):
    delay = seconds_per_step;
    steps = int(seconds / seconds_per_step / StepCount);
    print(str(steps))
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
    setStep(0,0,0,0)

def backwards(seconds):
    delay = seconds_per_step;
    steps = int(seconds_per_step * seconds / StepCount);
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
    setStep(0,0,0,0)

if __name__ == '__main__':
    setStep(0,0,0,0)
    print("Delay: {}".format(seconds_per_step))
    while True:
        seconds = raw_input("How many seconds forward? ")
        forward(int(seconds))
        seconds = raw_input("How many seconds backwards? ")
        backwards(int(seconds))