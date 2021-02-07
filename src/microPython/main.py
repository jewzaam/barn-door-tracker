from machine import Pin
import utime as time
import math
import ujson as json

CONFIG_FILENAME="stepper.json"
pins={}
config={}
totals={
    'enabled': False,
    'ms': 0,
    'steps': 0
}

def load_config():
    config={}
    with open(CONFIG_FILENAME, 'r') as f:
        config=json.loads(f.read())
    return config

def tick():
    # get some tick metric, diff_ms must handle the unit
    return time.ticks_us()

def diff_ms(now, then):
    global totals
    # see tick() for units
    diff_ms=time.ticks_diff(now, then) / 1000.0
    if totals['enabled']:
        totals['ms']+=diff_ms
    return diff_ms

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
    global pins,config

    print("STARTUP")

    has_startup=False

    for key in config['gp_out'].keys():
        value=config['gp_out'][key]
        if key == "startup_gp_on":
            # special case, we handle it later
            has_startup=True
        elif isinstance(value,list):
            pins[key]=[]
            for g in value:
                pins[key].append(Pin(g, Pin.OUT))
        else:
            pins[key]=Pin(value, Pin.OUT)

    if has_startup:
        for key in config['gp_out']['startup_gp_on']:
            pins[key].on()

def shutdown(step_delay_ms):
    global config

    # Shut it down!
    for key in pins.keys():
        value=pins[key]
        if isinstance(value,list):
            for pin in value:
                pin.off()
        else:
            pins[key].off()
    
    # print how we did, in case someone is watching
    print("total_steps: {}".format(totals['steps']))
    if totals['ms'] > 0:
        total_delta_ms=totals['ms'] - (totals['steps'] * step_delay_ms)
        total_error_p=math.floor(total_delta_ms/totals['ms']*10000.0)/100.0
        print("total_ms: {}".format(totals['ms']))
        print("total_delta_ms: {}".format(total_delta_ms))
        print("total_error: {} %".format(total_error_p))
    else:
        print("WARNING: not enough time to collect overall timing metrics")
    print("")
    print("SHUTDOWN")

def setOutput(values):
    for i in range(0, len(values)):
        pins['stepper'][i].value(values[i])

def calibrate_delay(expected_duration_ms,step_delay_ms,step_count,start_tick,end_tick):
    global config

    # default to the current delay, in case we decide not to calculate a new one
    calibrated_delay_ms = step_delay_ms

    # get the actual duration of the calibration iteration
    actual_duration_ms = diff_ms(end_tick, start_tick)
    
    # how far off is the actual from expected:
    calibration_factor = actual_duration_ms / expected_duration_ms

    if config['debug']:
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

        if config['debug']:
            print("ahead_ms: {}".format(actual_duration_ms - expected_duration_ms))
            print("momentary_error: {} %".format(math.floor((1-actual_duration_ms/expected_duration_ms)*10000.0)/100.0))
            print("calibrated_delay_ms: {}".format(calibrated_delay_ms))

    if config['debug']:
        print("")

    return calibrated_delay_ms

def forward(step_delay_ms):
    global config,totals

    calibration_target=config['calibration']['accuracy']
    sequence=config['tracker']['stepper']['sequence']
    sequence_len=len(sequence)

    # the value we get for step delay is our ideal / target value
    # it will be recalcuated to adjust for real time as we can't get 100% accurate by just saying "sleep X ms"
    # so, keep that ideal value stashed for calculations
    target_ms_per_step = step_delay_ms

    # to minimize oscillation and increase accuracy:
    # * calibration is done on a short cycle
    # * calibration step and time is reset each cycle
    # * calibration cycle aligns with sequence (don't cut a sequence in half!)

    # how many steps to use for each calibration
    calibration_frequency = 50 * sequence_len

    calibration_start_tick = tick()
    calibration_step = 1

    if config['debug']:
        print("calibration_start_tick: {}".format(calibration_start_tick))
        print("calibration_frequency: {}".format(calibration_frequency))
        print("")

    while True:
        # get the values for each stepper coil and set them
        sequence_values=sequence[calibration_step%sequence_len]
        for i in range(0, len(sequence_values)):
            pins['stepper'][i].value(sequence_values[i])

        if calibration_step%calibration_frequency == 0:
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
            calibration_step = calibration_step % sequence_len
            calibration_start_tick = now_tick

            # turn off Pico LED once we're within calibration target
            calibration_p=abs(1.0 - (step_delay_ms / calibrated_delay_ms))
            if calibration_p < calibration_target:
                # start the "totals" (we only care about post-calibration)
                totals['enabled']=True
                # and turn off any pins we should turn off
                for pin_key in config['calibration']['calibrated_gp_off']:
                    pins[pin_key].off()

            step_delay_ms = calibrated_delay_ms
            if config['debug']:
                # useful overall stats for verifying calibration is doing what it should: keep the TOTAL drift (delta) down.
                # note this is always shown on shutdown even if debug is disabled
                total_delta_ms=totals['ms'] - (calibration_step * target_ms_per_step)

                if totals['ms'] > 0.0:
                    total_error_p=math.floor(total_delta_ms/totals['ms']*10000.0)/100.0
                else:
                    total_error_p="UNKNOWN"

                print("total_steps: {}".format(totals['steps']))
                print("total_ms: {}".format(totals['ms']))
                print("total_delta_ms: {}".format(total_delta_ms))
                print("total_error: {} %".format(total_error_p))
                print("")

        # use custom sleep, it's a busy wait.  specify accuracy < 100% else all sleeps are LONGER than target. 99% is pretty good
        usleep(step_delay_ms*1000.0,0.99)
        # increment global step, used only for "total" debug and shutdown info
        if totals['enabled']:
            totals['steps']+=1
        # increment the calibration step
        calibration_step = calibration_step + 1

if __name__ == '__main__':
    # TODO load the initial step delay from configuration
    step_delay_ms=4.633737
    config=load_config()
    
    try:
        # fire up power and pico's LED (just so we know it should be doing something)
        startup()
        forward(step_delay_ms)
    except KeyboardInterrupt:
        pass
    finally:
        # abort abort! turn off all output and print metrics
        shutdown(step_delay_ms)
