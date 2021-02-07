from machine import Pin, Timer
import utime as time
import math
import ujson as json

# this is READ ONLY!
READ_CONFIG_FILENAME="stepper.json"
WRITE_CONFIG_FILENAME="output-stepper.json"
pins_out={}
pins_in={}
input_state={}
config={}
totals={
    'enabled': False,
    'actual_ms': 0,
    'expected_ms': 0,
    'steps': 0
}
control={
    "forward": 1,
    "reverse": 0,
    "stop": 0,
    "faster": 0,
    "slower": 0,
    "status": 0,
    "locked": True,
    "step_delay_ms": -1,
    "radius": -1
}

def print_totals():
    # print how we did, in case someone is watching
    print("total_steps: {}".format(totals['steps']))
    if totals['actual_ms'] > 0:
        total_delta_ms=totals['actual_ms'] - totals['expected_ms']
        total_error_p=math.floor(total_delta_ms/totals['expected_ms']*10000.0)/100.0
        print("total_actual_ms: {}".format(totals['actual_ms']))
        print("total_expected_ms: {}".format(totals['expected_ms']))
        print("total_delta_ms: {}".format(total_delta_ms))
        print("total_error: {} %".format(total_error_p))
    else:
        print("WARNING: not enough time to collect overall timing metrics")
    print("")

def load_config():
    config={}
    with open(READ_CONFIG_FILENAME, 'r') as f:
        config=json.loads(f.read())
    return config

def save_config():
    config={}
    with open(WRITE_CONFIG_FILENAME, 'w') as f:
        f.write()
        config=json.loads(f.read())
    return config

def tick():
    # get some tick metric, diff_ms must handle the unit
    return time.ticks_us()

def diff_ms(now,then):
    # see tick() for units
    return time.ticks_diff(now, then) / 1000.0

def usleep(us,accuracy=0.99):
    usleep_from(time.ticks_us(),us,accuracy)

def usleep_from(start_tick,us,accuracy=0.99):
    diff = 0
    now = start_tick
    
    # loop until we're within the given accuracy or have gone over
    while diff < us and abs(diff/us)<accuracy:
        now = time.ticks_us()
        diff = time.ticks_diff(now,start_tick)

    return now

def startup():
    global pins_out,config

    print("STARTUP")

    has_startup=False

    # initialize output pins
    for key in config['gp_out'].keys():
        value=config['gp_out'][key]
        if key == "startup_gp_on":
            # special case, we handle it later
            has_startup=True
        elif isinstance(value,list):
            pins_out[key]=[]
            for g in value:
               pins_out[key].append(Pin(g, Pin.OUT))
        else:
            pins_out[key]=Pin(value, Pin.OUT)

    # turn on the "on startup" outputs
    if has_startup:
        for key in config['gp_out']['startup_gp_on']:
            pins_out[key].on()

    # initalize input pins
    for key in config['gp_in'].keys():
        value=config['gp_in'][key]
        pins_in[key]=Pin(value, Pin.IN, Pin.PULL_DOWN)

    # INITIALIZE STATE
    # lock controls
    input_state['lock']=tick()
    # start with configured radius
    control['radius']=config['tracker']['radius']

def read_in():
    global input_state
    # read all the input pins and update status.
    # does not make any changes

    for key in pins_in.keys():
        pin=pins_in[key]
        value=pin.value()
        if value>0:
            # input is on
            if input_state[key]<=0:
                # input was not previously on, capture when it turned on
                input_state[key]=tick()
        else:
            # input is off, (blindly) clear state
            input_state[key]=0

def update_lock():
    # if the lock input has been on long enough toggle lock state

    # if the lock state is not on, do nothing.. there is no possible attempt at unlock
    if input_state['lock']<=0:
        return
    
    # check how long it has been on
    lock_ms=diff_ms(tick(),input_state["lock"])
    if lock_ms >= float(config['controls']['hold_lock_s'])*1000.0:
        # lock button on long enough, toggle lock
        # but only if the tick is different
        if 'lock_tick' not in control or control['lock_tick']!=input_state["lock"]:
            control['locked']=not control['locked']
            control['lock_tick']=input_state["lock"]

            # don't toggle the "status" input, explicitly set value in control so this press is ignored
            # TODO be smarter about this, check if lock and status are on the same input
            control['status']=input_state['status']
            # toggle any lock output
            if 'lock' in pins_out:
                # output can be LED to warn of unlock
                pin=pins_out['lock']
                if not control['locked']:
                    pin.on()
                else:
                    pin.off()
            if control['locked']:
                # when we lock, force direction to forward and configure delay
                control['stop']=0
                control['reverse']=0
                control['forward']=1
                configure_step_delay_ms()
            else:
                # when unlocked, stop
                control['stop']=1
            print("STATE changed: locked={}".format(control['locked']))

def handle_input():
    global config

    # if locked, do nothing. ever.
    if control['locked']:
        return

    # quick note on the "control" structure...
    # I have 3 booleans for state simply so it's explicit and easier to read.
    # It is not efficient or flexible and I don't care.

    # handle the various inputs
    # use the input tick (input_state value) to ensure only trigger on an input state change and don't flap

    calculate_delay=False
    led=pins_out['led']

    if input_state['forward'] > 0:
        # "forward" is pushed!
        if control['forward'] > 0 and control['forward'] != input_state['forward'] and control['stop'] == 0:
            # already going forward.  stop!
            control['stop']=input_state['forward']
            control['forward']=input_state['forward'] # ensure we don't flip out of stop on next check
            control['reverse']=0
        elif (control['forward'] == 0 or control['forward'] != input_state['forward']):
            # not going foward.. so let's do that
            control['stop']=0
            control['forward']=input_state['forward']
            control['reverse']=0
            calculate_delay=True

    if input_state['reverse'] > 0:
        # "reverse" is pushed!
        if control['reverse'] > 0 and control['reverse'] != input_state['reverse'] and control['stop'] == 0:
            # already going reverse.  stop!
            control['stop']=input_state['reverse']
            control['forward']=0
            control['reverse']=input_state['reverse'] # ensure we don't flip out of stop on next check
        elif (control['reverse'] == 0 or control['reverse'] != input_state['reverse']):
            # not going reverse.. so let's do that
            control['stop']=0
            control['forward']=0
            control['reverse']=input_state['reverse']
            calculate_delay=True

    if input_state['faster'] > 0 and control['faster'] != input_state['faster']:
        # "faster" is pushed!
        # increment the radius of the tracker
        control['radius']+=config['controls']['faster_increment']
        control['faster']=input_state['faster']
        calculate_delay=True
        # small visual indicator
        led.toggle()
        usleep(100000)
        led.toggle()

    if input_state['slower'] > 0 and control['slower'] != input_state['slower']:
        # "slower" is pushed!
        # decrement the radius of the tracker
        control['radius']-=config['controls']['slower_increment']
        control['slower']=input_state['slower']
        calculate_delay=True
        # small visual indicator
        led.toggle()
        usleep(100000)
        led.toggle()

    if input_state['status'] > 0 and control['status'] != input_state['status']:
        # "status" (push down) is pushed!
        # show how much the radius is modified.. 
        # blink LED fast for increased speed / radius
        # blink LED slow for decreased speed / radius
        original=led.value()
        led.off()
        usleep(1000000) # 1 second
        # how much change
        radius_delta=control['radius']-config['tracker']['radius']
        blink_delay_ms=0
        blink_count=0
        if radius_delta > 0:
            # radius increased
            blink_delay_ms=50.0
            blink_count=abs(radius_delta)/config['controls']['faster_increment']
        elif radius_delta < 0:
            # radius decreasd
            blink_delay_ms=500.0
            blink_count=abs(radius_delta)/config['controls']['slower_increment']
        for i in range(0,blink_count-1):
            led.on()
            usleep(blink_delay_ms*1000.0)
            led.off()
            usleep(500000.0)
        led.off()
        usleep(1000000) # 1 second
        led.value(original)

    # update the control (ideal) step delay
    if calculate_delay:
        configure_step_delay_ms()

def shutdown():
    global config

    # Shut it down!
    for key in pins_out.keys():
        value=pins_out[key]
        if isinstance(value,list):
            for pin in value:
                pin.off()
        else:
            pins_out[key].off()
    
    # print how we did, in case someone is watching
    print_totals()
    print("SHUTDOWN")

def configure_step_delay_ms():
    # calculate steps per revolution of the stepper
    stepper_gear_1=float(config['stepper']['gear_ratio'].split(":")[0])
    stepper_gear_2=float(config['stepper']['gear_ratio'].split(":")[1])
    stepper_gear_ratio=stepper_gear_1/stepper_gear_2
    stepper_steps_per_rev=360.0 / config['stepper']['stride_angle'] * stepper_gear_ratio

    # calculate steps per revolution of the trackre
    tracker_radius=float(control['radius'])
    tracker_pitch=float(config['tracker']['pitch'])
    tracker_gear_1=float(config['tracker']['gear_ratio'].split(":")[0])
    tracker_gear_2=float(config['tracker']['gear_ratio'].split(":")[1])
    tracker_gear_ratio=tracker_gear_1/tracker_gear_2
    tracker_steps_per_rev=stepper_steps_per_rev / tracker_gear_ratio

    tracker_circumference=tracker_radius*2*math.pi

    target_mm_per_ms=tracker_circumference/config['sidereal_ms']
    target_steps_per_mm=tracker_steps_per_rev/tracker_pitch
    target_steps_per_ms=target_mm_per_ms*target_steps_per_mm
    ideal_step_delay_ms=1.0/target_steps_per_ms

    # adjust for reverse
    if control['reverse']:
        # use max rpm to calculate the  fastest we can reverse.
        ideal_step_delay_ms = config['controls']['reverse_step_delay_ms']

    if config['debug']:
        print("stepper_steps_per_rev: {}".format(stepper_steps_per_rev))
        print("tracker_steps_per_rev: {}".format(tracker_steps_per_rev))
        print("tracker_circumference: {}".format(tracker_circumference))
        print("target_mm_per_ms: {}".format(target_mm_per_ms))
        print("ideal_step_delay_ms: {}".format(ideal_step_delay_ms))
        print("")

    print("step_delay_ms => {}".format(ideal_step_delay_ms))
    control['step_delay_ms']=ideal_step_delay_ms

def calibrate_delay(expected_duration_ms,step_delay_ms,step_count,start_tick,end_tick):
    global config

    # default to the current delay, in case we decide not to calculate a new one
    calibrated_delay_ms = step_delay_ms

    # get the actual duration of the calibration iteration
    actual_duration_ms = diff_ms(end_tick, start_tick)

    # increment totals 
    if totals['enabled']:
        totals['actual_ms']+=actual_duration_ms
        totals['expected_ms']+=expected_duration_ms
    
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

def control_loop():
    global config,totals

    # set initial step delay and ensure loop will pick it up
    configure_step_delay_ms()
    ideal_step_delay_ms=-1 # the ideal value
    step_delay_ms=ideal_step_delay_ms # the actual value used for sleep

    calibration_target=config['calibration']['accuracy']
    sequence=config['stepper']['sequence']
    sequence_len=len(sequence)

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
        # get latest value for the step delay
        if ideal_step_delay_ms != control['step_delay_ms']:
            # snag the new value
            step_delay_ms=control['step_delay_ms']
            # reset the ideal
            ideal_step_delay_ms = step_delay_ms
            # reset totals since configuration has changed
            totals['enabled']=False
            # turn on calibration output (if there is any)
            for pin_key in config['calibration']['calibrated_gp_off']:
                pins_out[pin_key].on()
            # print the current control settings since this changed
            # we will be calibrating so this small overhead is OK
            print("control: {}".format(str(control)))

        # capture the tick BEFORE changing stepper state.
        # this is used as the starting reference for usleep_from
        # and we include the time to change the stepper coils for better accuracy
        # (else you have stepper change outside of delay and you get drift)
        usleep_start_tick=tick()

        # move the stepper if we are not stopped
        if not control['stop']:
            # get the values for each stepper coil and set them, account for reverse
            sequence_index=calibration_step%sequence_len
            if control['reverse']>0:
                sequence_index=(sequence_len-sequence_index)%sequence_len
            #print("sequence_index: {}".format(sequence_index))
            sequence_values=sequence[sequence_index]

            # update stepper coil outputs if not stopped
            if control['stop'] == 0:
                for i in range(0, len(sequence_values)):
                    pins_out['stepper'][i].value(sequence_values[i])

            if calibration_step%calibration_frequency == 0:
                # calibrate_delay(expected_duration_ms,step_delay_ms,step_count,start_time_ms,end_time_ms):
                expected_duration_ms = calibration_step * ideal_step_delay_ms
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
                if not totals['enabled'] and calibration_p < calibration_target:
                    print("calibration accuracy met ({}%), step_delay_ms={}".format(calibration_p,calibrated_delay_ms))
                    # start the "totals" (we only care about post-calibration)
                    totals['enabled']=True
                    totals['actual_ms']=0
                    totals['expected_ms']=0
                    # and turn off any pins we should turn off
                    for pin_key in config['calibration']['calibrated_gp_off']:
                        pins_out[pin_key].off()

                # update step delay AFTER checking accuracy... (doh!)
                step_delay_ms = calibrated_delay_ms

                if config['debug'] and totals['enabled']:
                    print_totals()

            # increment global step, used only for "total" debug and shutdown info
            if totals['enabled']:
                totals['steps']+=1
            # increment the calibration step
            calibration_step = calibration_step + 1

        # done moving stepper.  do input and sleep

        # read all the inputs
        read_in()

        # handle lock
        update_lock()

        # handle input stuff (if unlocked)
        handle_input()

        # use custom sleep, it's a busy wait.  specify accuracy < 100% else all sleeps are LONGER than target. 99% is pretty good
        usleep_from(usleep_start_tick,step_delay_ms*1000.0,0.99)

if __name__ == '__main__':
    # TODO load the initial step delay from configuration
    config=load_config()
    
    try:
        # fire up power and pico's LED (just so we know it should be doing something)
        startup()
        
        # the main control loop, does all the things...
        control_loop()
    except KeyboardInterrupt:
        pass
    finally:
        # abort abort! turn off all output and print metrics
        shutdown()
