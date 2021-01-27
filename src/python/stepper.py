import RPi.GPIO as GPIO
import time

debug = True

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
enable_pin = 18

# Order in datasheet: orange, yellow, pink, blue, red (always 0)
# https://components101.com/motors/28byj-48-stepper-motor

# pins in order per data sheet: orange, yellow, pink, blue
Pins = [17,24,4,23]

# datasheet has stride angle at 5.625, but this is not quite right.
motor_stride_angle=5.63 # degrees per step
motor_gear_ratio=64 # 64:1 internal gear ratio (motor to shaft)
motor_steps_per_rev = 360/motor_stride_angle * motor_gear_ratio

external_gear_ratio = 10.0/43.0 # motor drives 10 tooth gear, driving 43 tooth gear
external_steps_per_rev = motor_steps_per_rev / external_gear_ratio

# goal is 1 rev per minute.  could adjust to be flexible if needed by adding a param for the seconds
seconds_per_step = 60.0 / external_steps_per_rev
ms_per_step = seconds_per_step * 1000.0

tested_initial_delay_ms=3.3

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

def startup():
    GPIO.setup(enable_pin, GPIO.OUT)
    for pin in Pins:
        GPIO.setup(pin, GPIO.OUT)
    # go ahead and turn on power
    GPIO.output(enable_pin, 1)

def shutdown():
    for pin in Pins:
        GPIO.output(pin, 0)
    GPIO.output(enable_pin, 0)

def setOutput(values):
    for i in range(len(Pins)):
        GPIO.output(Pins[i], values[i])

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
        print("step_count: {}".format(step_count))
        print("ahead_ms: {}".format(actual_duration_ms - expected_duration_ms))
        print("calibration_factor: {}".format(calibration_factor))
        print("calibrated_delay_ms: {}".format(calibrated_delay_ms))

    return calibrated_delay_ms

def forward():
    # initial delay is the calculated time per step
    step_delay_ms = tested_initial_delay_ms

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
            expected_duration_ms = calibration_step * ms_per_step # this NEVER changes
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
                print("total_delta_ms: {}".format(now - start_time_ms - (step * ms_per_step)))
                print("total_steps: {}".format(step))
                print("total_time_s: {}".format((now-start_time_ms)/1000))

        time.sleep(step_delay_ms/1000.0)
        step = step + 1
        calibration_step = calibration_step + 1

if __name__ == '__main__':
    try:
        startup()
        forward()
    finally:
        shutdown()