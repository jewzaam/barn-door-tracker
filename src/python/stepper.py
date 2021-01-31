import RPi.GPIO as GPIO
import time
import math

debug = False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# To calculate target revolutions per minute of the rod gear we need...
tracker_radius_mm=200.0
tracker_threads_per_mm=20.0/25.4 # 20 threads per inch

# Order in datasheet: orange, yellow, pink, blue, red (always 0)
# https://components101.com/motors/28byj-48-stepper-motor
 
gpio_power = 18

# pins in order per data sheet: orange, yellow, pink, blue
gpio_coils=[24,23,17,4]

# adjust if different
Sequence = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1],
]
SequenceCount = len(Sequence)

# Motor data:
motor_stride_angle=5.625 # degrees per step
motor_gear_ratio=64.0 # 64:1 internal gear ratio (motor to shaft)

# Gear data:
external_gear_stepper=10.0
external_gear_rod=43.0

# Steps per revolution:
motor_steps_per_rev = 360.0/motor_stride_angle * motor_gear_ratio
external_steps_per_rev = motor_steps_per_rev / (external_gear_stepper / external_gear_rod)

# Calculate initial stepper delay.
target_rev_per_minute=(tracker_radius_mm*2*math.pi/1440.0)/tracker_threads_per_mm
target_steps_per_minute=external_steps_per_rev*target_rev_per_minute
target_minutes_per_step=(1/target_steps_per_minute)
target_ms_per_step=target_minutes_per_step*60000.0

if debug:
    print("tracker_threads_per_mm: {}".format(tracker_threads_per_mm))
    print("motor_steps_per_rev: {}".format(motor_steps_per_rev))
    print("external_steps_per_rev: {}".format(external_steps_per_rev))
    print("target_rev_per_minute: {}".format(target_rev_per_minute))
    print("target_steps_per_minute: {}".format(target_steps_per_minute))
    print("target_minutes_per_step: {}".format(target_minutes_per_step))
    print("target_ms_per_step: {}".format(target_ms_per_step))
    print("")


def startup():
    GPIO.setup(gpio_power, GPIO.OUT)
    for pin in gpio_coils:
        GPIO.setup(pin, GPIO.OUT)
    # go ahead and turn on power
    GPIO.output(gpio_power, 1)

def shutdown():
    for pin in gpio_coils:
        GPIO.output(pin, 0)
    GPIO.output(gpio_power, 0)

def setOutput(values):
    for i in range(len(gpio_coils)):
        GPIO.output(gpio_coils[i], values[i])

def calibrated_delay(expected_duration_ms,step_delay_ms,step_count,start_time_ms,end_time_ms):
    calibrated_delay_ms = step_delay_ms
    actual_duration_ms = end_time_ms - start_time_ms
    
    # how far off is the actual from expected:
    calibration_factor = actual_duration_ms / expected_duration_ms

    # pick new delay...
    calculated_delay_ms = step_delay_ms / calibration_factor

    # average the current delay and calculated to try to stop oscillation
    calibrated_delay_ms = (calculated_delay_ms + step_delay_ms) / 2

    if debug:
        print("step_delay_ms: {}".format(step_delay_ms))
        print("step_count: {}".format(step_count))
        print("ahead_ms: {}".format(actual_duration_ms - expected_duration_ms))
        print("momentary_error: {} %".format(math.floor((1-actual_duration_ms/expected_duration_ms)*10000.0)/100.0))
        print("calibration_factor: {}".format(calibration_factor))
        print("calibrated_delay_ms: {}".format(calibrated_delay_ms))

    return calibrated_delay_ms

def forward():
    # initial delay is the calculated time per step
    step_delay_ms = target_ms_per_step

    # capture start time for calibration
    start_time_ms = time.time() * 1000.0

    # to minimize oscillation and get a 0.024% accuracy in my testing:
    # * calibration is done on a short cycle
    # * calibration step and time is reset each cycle
    # * calibration cycle aligns with sequence (don't cut a sequence in half!)

    # how many steps to use for each calibration
    calibration_frequency = 50 * SequenceCount

    calibration_start_time_ms = time.time() * 1000.0
    step = 1
    calibration_step = 1
    while True:
        setOutput(Sequence[step%SequenceCount])

        if step%calibration_frequency == 0:
            # calibrated_delay(expected_duration_ms,step_delay_ms,step_count,start_time_ms,end_time_ms):
            expected_duration_ms = calibration_step * target_ms_per_step # this NEVER changes
            now = time.time() * 1000.0
            calibrated_delay_ms = calibrated_delay(
                    expected_duration_ms,
                    step_delay_ms,
                    calibration_step,
                    calibration_start_time_ms,
                    now
                )
            # reset calibration window
            calibration_step = step % SequenceCount
            calibration_start_time_ms = time.time() * 1000.0

            step_delay_ms = calibrated_delay_ms
            if debug:
                # useful overall stats for verifying calibration is doing what it should: keep the TOTAL drift (delta) down.
                total_time_ms=now-start_time_ms
                total_delta_ms=now - start_time_ms - (step * target_ms_per_step)
                total_error_p=math.floor(total_delta_ms/total_time_ms*10000.0)/100.0
                print("total_steps: {}".format(step))
                print("total_time_ms: {}".format(total_time_ms))
                print("total_delta_ms: {}".format(total_delta_ms))
                print("total_error: {} %".format(total_error_p))
                print("")

        time.sleep(step_delay_ms/1000.0)
        step = step + 1
        calibration_step = calibration_step + 1

if __name__ == '__main__':
    try:
        startup()
        forward()
    finally:
        shutdown()