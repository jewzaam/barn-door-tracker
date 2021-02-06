from machine import Pin
import utime as time
import math

# WARNING printing on the pico makes a big difference in sleep accuracy.  use debug with caution!
debug = False

# global total steps taken
step=0

# Order in datasheet: orange, yellow, pink, blue, red (always 0)
# https://components101.com/motors/28byj-48-stepper-motor
 
gpio_power = 18
pin_power = Pin(gpio_power, Pin.OUT)
pin_led = Pin(25, Pin.OUT)

# pins in order per data sheet: orange, yellow, pink, blue
gpio_coils=[28,27,26,22]
pin_coils=[
    Pin(gpio_coils[0], Pin.OUT),
    Pin(gpio_coils[1], Pin.OUT),
    Pin(gpio_coils[2], Pin.OUT),
    Pin(gpio_coils[3], Pin.OUT)
]

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

def tick():
    # get some tick metric, diff_ms must handle the unit
    return time.ticks_us()

def diff_ms(now, then):
    # see tick() for units
    return time.ticks_diff(now, then) / 1000.0

def usleep(us,accuracy=0.99):
    start = time.ticks_us()
    diff = 0
    now = start
    
    # loop until we're within the given accuracy or have gone over
    while diff < us and abs(diff/us)<accuracy:
        now = time.ticks_us()
        diff = time.ticks_diff(now,start)

    return now

def startup():
    print("STARTUP")
    pin_led.on()
    pin_power.on()

def shutdown(step_delay_ms,start_tick):
    for pin in pin_coils:
        pin.off()
    pin_power.off()
    pin_led.off()
    
    # print how we did, in case someone is watching
    now_tick=tick()
    total_time_ms=diff_ms(now_tick,start_tick)
    total_delta_ms=total_time_ms - (step * step_delay_ms)

    if total_time_ms > 0.0:
        total_error_p=math.floor(total_delta_ms/total_time_ms*10000.0)/100.0
    else:
        total_error_p="UNKNOWN"

    print("total_steps: {}".format(step))
    print("total_time_ms: {}".format(total_time_ms))
    print("total_delta_ms: {}".format(total_delta_ms))
    print("total_error: {} %".format(total_error_p))
    print("")
    print("SHUTDOWN")

def setOutput(values):
    i = 0
    for pin in pin_coils:
        pin.value(values[i])
        i = i + 1

def calibrate_delay(expected_duration_ms,step_delay_ms,step_count,start_tick,end_tick):
    # default to the current delay, in case we decide not to calculate a new one
    calibrated_delay_ms = step_delay_ms

    # get the actual duration of the calibration iteration
    actual_duration_ms = diff_ms(end_tick, start_tick)
    
    # how far off is the actual from expected:
    calibration_factor = actual_duration_ms / expected_duration_ms

    if debug:
        print("expected_duration_ms: {}".format(expected_duration_ms))
        print("actual_duration_ms: {}".format(actual_duration_ms))
        print("step_delay_ms: {}".format(step_delay_ms))
        print("step_count: {}".format(step_count))
        print("start_tick: {}".format(int(start_tick)))
        print("end_tick: {}".format(int(end_tick)))
        print("calibration_factor: {}".format(calibration_factor))

    # do not adjust delay if any of these is true:
    #   we have a zero calibration factor
    #   calibration factor is very small (things are accurate enough)
    if calibration_factor != 0.0 and abs(calibration_factor - 1.0) > 0.001:
        # pick new delay...
        calculated_delay_ms = step_delay_ms / calibration_factor

        # average the current delay and calculated to try to reduce oscillation
        calibrated_delay_ms = (calculated_delay_ms + step_delay_ms) / 2

        if debug:
            print("ahead_ms: {}".format(actual_duration_ms - expected_duration_ms))
            print("momentary_error: {} %".format(math.floor((1-actual_duration_ms/expected_duration_ms)*10000.0)/100.0))
            print("calibrated_delay_ms: {}".format(calibrated_delay_ms))

    if debug:
        print("")

    return calibrated_delay_ms

def forward(calibration_target,step_delay_ms,start_tick):
    global step

    # the value we get for step delay is our ideal / target value
    # it will be recalcuated to adjust for real time as we can't get 100% accurate by just saying "sleep X ms"
    # so, keep that ideal value stashed for calculations
    target_ms_per_step = step_delay_ms

    # to minimize oscillation and increase accuracy:
    # * calibration is done on a short cycle
    # * calibration step and time is reset each cycle
    # * calibration cycle aligns with sequence (don't cut a sequence in half!)

    # how many steps to use for each calibration
    calibration_frequency = 50 * SequenceCount

    calibration_start_tick = start_tick
    step = 1
    calibration_step = 1

    if debug:
        print("calibration_start_tick: {}".format(calibration_start_tick))
        print("calibration_frequency: {}".format(calibration_frequency))
        print("")

    while True:
        setOutput(Sequence[step%SequenceCount])

        if step%calibration_frequency == 0:
            # calibrate_delay(expected_duration_ms,step_delay_ms,step_count,start_time_ms,end_time_ms):
            expected_duration_ms = calibration_step * target_ms_per_step
            now_tick = tick()
            calibrated_delay_ms = calibrate_delay(
                    expected_duration_ms,
                    step_delay_ms,
                    calibration_step,
                    calibration_start_tick,
                    now_tick
                )
            # reset calibration window (be sure not to jump in the sequence, use modulus)
            calibration_step = step % SequenceCount
            calibration_start_tick = now_tick

            # turn off Pico LED once we're within calibration target
            calibration_p=abs(1.0 - (step_delay_ms / calibrated_delay_ms))
            if calibration_p < calibration_target:
                pin_led.off()

            step_delay_ms = calibrated_delay_ms
            if debug:
                # useful overall stats for verifying calibration is doing what it should: keep the TOTAL drift (delta) down.
                # note this is always shown on shutdown even if debug is disabled
                total_time_ms=diff_ms(now_tick,start_tick)
                total_delta_ms=total_time_ms - (step * target_ms_per_step)

                if total_time_ms > 0.0:
                    total_error_p=math.floor(total_delta_ms/total_time_ms*10000.0)/100.0
                else:
                    total_error_p="UNKNOWN"

                print("total_steps: {}".format(step))
                print("total_time_ms: {}".format(total_time_ms))
                print("total_delta_ms: {}".format(total_delta_ms))
                print("total_error: {} %".format(total_error_p))
                print("")

        # use custom sleep, it's a busy wait.  specify accuracy < 100% else all sleeps are LONGER than target. 99% is pretty good
        usleep(step_delay_ms*1000.0,0.99)
        # increment global step, used only for "total" debug and shutdown info
        step = step + 1
        # increment the calibration step
        calibration_step = calibration_step + 1

if __name__ == '__main__':
    # TODO load the initial step delay from configuration
    calibration_target=0.001
    step_delay_ms=4.633737
    start_tick=tick()
    try:
        # fire up power and pico's LED (just so we know it should be doing something)
        startup()
        forward(calibration_target,step_delay_ms,start_tick)
    except KeyboardInterrupt:
        pass
    finally:
        # abort abort! turn off all output and print metrics
        shutdown(step_delay_ms,start_tick)
