from machine import Pin, Timer
import utime as time
import math
import ujson as json

# this is READ ONLY!
READ_CONFIG_FILENAME="stepper.json"
WRITE_CONFIG_FILENAME="output-stepper.json"
pins_out={}
pins_in={}
config={}

control={
    "forward": 1,
    "locked": True,
    "step_delay_ms": -1,
    "radius": -1,
    "step": 0,
    "timer": {
        "last_start_tick": 0,
        "current_start_tick": 0,
        "counter": 0,
        "expected_ms": 0,
        "actual_ms": 0,
        "last_ms": 0
    },
    "handlers": {
        "step": False,
        "status": False,
        "faster": False,
        "slower": False,
        "forward": False,
        "stop": False
    }
}
timers={}
status_blink_count=0

def load_config():
    config={}
    with open(READ_CONFIG_FILENAME, 'r') as f:
        config=json.loads(f.read())
    return config

def tick():
    # get some tick metric, diff_ms must handle the unit
    return time.ticks_us()

def diff_ms(now,then):
    # see tick() for units
    return time.ticks_diff(now, then) / 1000.0

def startup():
    global pins_out,config,logging_filename

    # initialize output pins
    for key in config['gp_out'].keys():
        value=config['gp_out'][key]
        if key == "startup_gp_on":
            # special case, we handle it later
            continue
        elif isinstance(value,list):
            pins_out[key]=[]
            for g in value:
               pins_out[key].append(Pin(g, Pin.OUT))
        else:
            pins_out[key]=Pin(value, Pin.OUT)

    # turn on the "on startup" outputs
    if 'startup_gp_on' in config['gp_out']:
        for key in config['gp_out']['startup_gp_on']:
            pins_out[key].on()

    # initalize input handlers
    for key in config['gp_in'].keys():
        gpio=config['gp_in'][key]['gpio']
        pin=Pin(gpio, Pin.IN, Pin.PULL_DOWN)
        pins_in[key]=pin

    # initialize input handlers
    # since stop is disabled, forward is also disabled
    #pins_in['forward'].irq(trigger=Pin.IRQ_FALLING, handler=handle_up)
    # turns out it's SUPER annoying to have this stop when tuning speed.. removing for now
    #pins_in['stop'].irq(trigger=Pin.IRQ_FALLING, handler=handle_down)
    pins_in['faster'].irq(trigger=Pin.IRQ_FALLING, handler=handle_left)
    pins_in['slower'].irq(trigger=Pin.IRQ_FALLING, handler=handle_right)
    pins_in['lock'].irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_center)
    #pins_in['status'].irq(trigger=Pin.IRQ_FALLING, handler=handle_center)

        # INITIALIZE STATE
    # initialize lock
    control['locked']=config['start_locked']
    if not control['locked']:
        pins_out["lock"].on()
    # start with configured radius
    control['radius']=config['tracker']['radius']

    # start the timer
    setup_timer()

def setup_timer():
    configure_step_delay_ms()
    frequency=1000.0/control['step_delay_ms']

    # A Timer is used for triggering a step, but is not used to execute the step!
    # When a timer callback is executed the time in a callback the clock for the next trigger starts after returning.
    # The stepper takes about 250ms to update all 4 coils, therefore if done in the callback we're off by 250ms.
    # Instead, the callback updates a flag to indicate a step _should_ be taken, and this is handled in a hot loop.
    #
    # The callback to trigger a step is "trigger_step()".
    # The execution of a step is "do_step()".
    # The control loop watches for a control flat from trigger_step to then fire do_step.
    #
    # The timer callback is a simple as possible. 
    # See https://docs.micropython.org/en/latest/reference/isr_rules.html 

    # setup timer for steps
    if 'trigger_step' not in timers:
        timers["trigger_step"]=Timer()
    timers["trigger_step"].init(freq=frequency, mode=Timer.PERIODIC, callback=trigger_step)

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

    if config['debug']:
        print("stepper_steps_per_rev: {}".format(stepper_steps_per_rev))
        print("tracker_steps_per_rev: {}".format(tracker_steps_per_rev))
        print("tracker_circumference: {}".format(tracker_circumference))
        print("target_mm_per_ms: {}".format(target_mm_per_ms))
        print("ideal_step_delay_ms: {}".format(ideal_step_delay_ms))
        print("")

    if control['step_delay_ms']!=ideal_step_delay_ms:
        # it changed, update our control
        control['step_delay_ms']=ideal_step_delay_ms
        # and reset the last_start_tick to remove the last step iteration from totals, as it's now wrong.
        # note this doesn't matter for functionality of the tracker, just for `tick error` printed on shutdown
        control['timer']['last_start_tick']=0

def trigger_step(timer):
    global timer_tick
    timer_tick=tick()
    # capture the time the trigger was fired
    control['timer']['current_start_tick']=tick()
    # tell control loop we need to do a step if 'forward' is enabled
    control['handlers']['step']=control['forward']

def do_step():
    control['handlers']['step']=False

    # very basic, do a step
    sequence_values=config['stepper']['sequence'][control['step']]

    # update stepper coil outputs
    for i in range(0, len(sequence_values)):
        pins_out['stepper'][i].value(sequence_values[i])

    # setup next step
    control["step"]=(control["step"]+1)%len(config['stepper']['sequence'])

def shutdown():
    global config

    # turn off output pins
    for key in pins_out.keys():
        value=pins_out[key]
        if isinstance(value,list):
            for pin in value:
                pin.off()
        else:
            value.off()

    # disable all timers (deinit)
    for key in timers.keys():
        timers[key].deinit()

    # print minimal stats (useful for debugging / sanity checking)
    print_status()

def control_loop():
    global control

    while True:
        # Control loop basically executes a bunch of handlers in order of priority.
        # Each "do_X" function must toggle off the handler if it's appropriate!

        if control['handlers']['stop']:
            do_stop()

        if control['handlers']['step']:
            # do the step
            do_step()
            # collect metadata on status (don't allocate new memory, i.e. arrays)
            then=control['timer']['last_start_tick']
            now=control['timer']['current_start_tick']
            if then > 0 and now > 0:
                control['timer']['counter']+=1
                control['timer']['last_ms']=diff_ms(now,then)
                control['timer']['actual_ms']+=control['timer']['last_ms']
                control['timer']['expected_ms']+=control['step_delay_ms']
            control['timer']['last_start_tick']=now

        if control['handlers']['faster']:
            do_faster()

        if control['handlers']['slower']:
            do_slower()

        if control['handlers']['forward']:
            do_forward()

def led_toggle(timer):
    pins_out["led"].toggle()

# https://micronote.tech/2020/02/Timers-and-Interrupts-with-a-NodeMCU-and-MicroPython/
def debounce(pin):
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

def handle_up(pin):
    if control['locked'] or debounce(pin) is None:
        return
    
    control['handlers']['forward']=True

def do_forward():
    control['handlers']['forward']=False
    control['forward']=1

def handle_down(pin):
    if control['locked'] or debounce(pin) is None:
        return

    control['handlers']['stop']=True

def do_stop():
    control['handlers']['stop']=False
    control['forward']=0
    # reset the tick so we don't get any of the time while stopped
    # and do_step will just pick it up again
    control['timer']['last_start_tick']=0

def handle_left(pin):
    if control['locked'] or debounce(pin) is None:
        return

    control['handlers']['faster']=True

def do_faster():
    control['handlers']['faster']=False

    # increment the radius of the tracker
    control['radius']+=config['controls']['faster_increment']
    # setup the timer for steps, it calculates new delay
    setup_timer()
    # small visual indicator, toggle LED then set a timer to toggle again in 1 second
    if 'led' not in timers:
        timers['led']=Timer()
    pins_out["led"].off()
    timers['led'].init(mode=Timer.ONE_SHOT,period=500,callback=led_toggle)

def handle_right(pin):
    if control['locked'] or debounce(pin) is None:
        return

    control['handlers']['slower']=True

def do_slower():
    control['handlers']['slower']=False

    # decrement the radius of the tracker
    control['radius']-=config['controls']['slower_increment']
    # setup the timer for steps, it calculates new delay
    setup_timer()
    # small visual indicator, toggle LED then set a timer to toggle again in 1 second
    if 'led' not in timers:
        timers['led']=Timer()
    pins_out["led"].off()
    timers['led'].init(mode=Timer.ONE_SHOT,period=500,callback=led_toggle)

def handle_center(pin):
    if debounce(pin) is None:
        return

    # don't do a handler for lock, we need the pin state
    do_lock(pin)

    if not control['locked'] and pin.value()<=0:
        control['handlers']['status']=True

def do_lock(pin):
    # if locked
    #   if button is active
    #       start lock timer
    #   else
    #       cancel lock timer
    if pin.value()>0:
        if 'lock' not in timers:
            timers['lock']=Timer()
        timers['lock'].init(mode=Timer.ONE_SHOT,period=config['controls']['hold_lock_s']*1000,callback=toggle_lock)
    elif 'lock' in timers:
        timers['lock'].deinit()

def toggle_lock(timer):
    global status_blink_count

    control['locked']=not control['locked']
    if control['locked']:
        pins_out["lock"].off()
        
        # hate doing this here but I hate having more functions even more.
        # we are firing a timer in the future to setup a timer for blinking.
        # the initial delay encodes the direction of delta
        # the number of blinks encodes the amount of delta

        # how much off the original radius are we?
        radius_delta=control['radius']-config['tracker']['radius']

        # if the delta is positive we have added to radius, so tracker is faster.
        # if slower, do a long period without blinking (10 sec)
        # if faster, do a short period without blinking (2 sec)
        # if at default, do NO delay and blink 3 times

        blink_delay=0
        blink_count=3
        if radius_delta<0:
            blink_delay=10000
            blink_count=int(abs(radius_delta)/config['controls']['slower_increment'])
        elif radius_delta>0:
            blink_delay=2000
            blink_count=int(abs(radius_delta)/config['controls']['faster_increment'])

        # the lock blink count must be 2x the total blinks since it's a dumb toggle
        status_blink_count=blink_count*2

        if 'blink' not in timers:
            timers['blink']=Timer()
        timers['blink'].init(mode=Timer.ONE_SHOT,period=blink_delay,callback=status_timer)
    else:
        pins_out["lock"].on()

def status_timer(timer):
    global config,status_blink_count

    # if not locked, do nothing. ever.
    if not control['locked']:
        return

    # update our timer to fire periodically and toggle the led.
    if status_blink_count>0:
        timer.init(mode=Timer.PERIODIC,freq=config['controls']['status_blink_hz'],callback=status_blink)

def status_blink(timer):
    global status_blink_count
    pins_out["led"].toggle()
    status_blink_count-=1
    if status_blink_count<=0:
        # all done, shutdown the timer
        timer.deinit()

def print_status():
    timer_actual_ms=control['timer']['actual_ms']
    timer_expected_ms=control['timer']['expected_ms']
    timer_count=control['timer']['counter']
    print("")
    print(control)
    if timer_count>0:
        print("avg_actual_delay_ms: {}".format(timer_actual_ms/timer_count))
    if timer_actual_ms>0:
        err_p=(1.0-timer_expected_ms/timer_actual_ms)*100.0
        print("total_error_p: {}%".format(err_p)) # to 1/1000 of a percent

if __name__ == '__main__':
    # TODO load the initial step delay from configuration
    config=load_config()
    
    try:
        # fire up power, pico's LED, and start timer
        startup()

        # the main control loop, does all the things...
        control_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # unusual, print the stack by raising it
        raise e
    finally:
        # abort abort! turn off all output and print metrics
        shutdown()
