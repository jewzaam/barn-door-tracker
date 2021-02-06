import sys, getopt, os.path
import time, datetime
import math
import yaml

# Utility to configure initial values for the stepper code.

DEBUG = False
CONFIG_FILENAME="stepper.yaml"
DEFAULT_CALIBRATION_ITERATIONS=30
SIDEREAL_DAY_IN_MINUTES=86164100/60000.0 # sidereal day in ms converted to minutes: http://www.kylesconverter.com/time/days-(sidereal)-to-milliseconds

def error(msg):
    print("ERROR: {}".format(msg))

def help():
    print("TODO: help text")

def save(config):
    # update history
    if 'calculated_ms' in config['delays']:
        latest=None
        if len(config['history']) > 0:
            latest=config['history'][0]

        # assume structure of history is valid

        # create new history if any delays have changed OR we don't have any history
        create_history=False
        if latest is not None:
            for key in config['delays'].keys():
                h_value=latest[key]
                d_value=config['delays'][key]
                if h_value != d_value:
                    create_history=True
                    break
        else:
            create_history=True

        if create_history:
            new_history={}
            new_history['timestamp']=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            for key in config['delays'].keys():
                new_history[key]=config['delays'][key]
            config['history'].insert(0, new_history)

    with open(CONFIG_FILENAME, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

def load():
    config={}
    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, 'r') as infile:
            config=yaml.load(infile, Loader=yaml.FullLoader)

    # initialize requrired child objects and arrays
    objects = ['pins','delays']
    arrays = ['history']

    for obj in objects:
        if obj not in config:
            config[obj]={}
    for arr in arrays:
        if arr not in config:
            config[arr]=[]

    return config

def steps_per_revolution(stepper):
    output=-1
    if str(stepper).upper() == "28BYJ-48":
        motor_stride_angle=5.625 # degrees per step
        motor_gear_ratio=64.0 # 64:1 internal gear ratio (motor to shaft)
        output = 360.0/motor_stride_angle * motor_gear_ratio

    return output

def calculate_step_delay_ms(config):
    global DEBUG

    radius=float(config['radius'])
    pitch=float(config['pitch'])
    stepper=config['stepper']
    gear_ratio=config['gearRatio']

    motor_steps_per_rev=steps_per_revolution(stepper)

    gear_1=float(str(gear_ratio).split(":")[0])
    gear_2=float(str(gear_ratio).split(":")[1])
    external_steps_per_rev=motor_steps_per_rev / (gear_1/gear_2)

    tracker_circumference=radius*2*math.pi

    target_mm_per_minute=tracker_circumference/SIDEREAL_DAY_IN_MINUTES
    target_steps_per_mm=external_steps_per_rev/pitch
    target_steps_per_minute=target_mm_per_minute*target_steps_per_mm
    target_ms_per_step=60000.0/target_steps_per_minute

    if DEBUG:
        print("sidereal_day: {}h {}m {}s".format(math.floor(SIDEREAL_DAY_IN_MINUTES/60.0),math.floor(SIDEREAL_DAY_IN_MINUTES%60.0),math.floor(6000.0*(SIDEREAL_DAY_IN_MINUTES-math.floor(SIDEREAL_DAY_IN_MINUTES))/100)))
        print("external_steps_per_rev: {}".format(external_steps_per_rev))
        print("target_mm_per_minute: {}".format(target_mm_per_minute))
        print("target_steps_per_mm: {}".format(target_steps_per_mm))
        print("target_steps_per_minute: {}".format(target_steps_per_minute))
        print("target_ms_per_step: {}".format(target_ms_per_step))
        print("")

    return target_ms_per_step

def make_config(argv):
    global DEBUG

    config = load()

    try:
        opts, args = getopt.getopt(argv,"hdc:r:p:s:g:",
        ["help","debug","calibrate=","radius=","pitch=",
        "stepper=","gearRatio=","pin_v5=","pin_stepperCoils="])
    except getopt.GetoptError:
        help()
        sys.exit(1)

    calculate=False

    valid_config=True

    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt in ("-d", "--debug"):
            DEBUG = True
        elif opt in ("-c", "--calibrate"):
            config['calibrate']['iterations'] = arg
        elif opt in ("-r", "--radius"):
            if 'radius' not in config or config['radius'] != arg:
                config['radius'] = float(arg)
                calculate=True
        elif opt in ("-p", "--pitch"):
            if 'pitch' not in config or config['pitch'] != arg:
                config['pitch'] = float(arg)
                calculate=True
        elif opt in ("-s", "--stepper"):
            if 'stepper' not in config or config['stepper'] != arg:
                config['stepper'] = arg
                calculate=True
        elif opt in ("-g", "--gearRatio"):
            if 'gearRatio' not in config or config['gearRatio'] != arg:
                if len(arg.split(":")) != 2:
                    error("invalid format for '{}'".format(opt))
                    valid_config=False
                else:
                    config['gearRatio'] = str(arg)
                    calculate=True
        elif opt in ("--pin_v5"):
            config['pins']['v5'] = int(arg)
        elif opt in ("--pin_stepperCoils"):
            config['pins']['stepperCoils'] = []
            for coil in arg.split(","):
                config['pins']['stepperCoils'].append(int(coil))

    # make sure we have all the config
    if 'radius' not in config:
        error("'radius' not set")
        valid_config=False
    if 'pitch' not in config:
        error("'pitch' not set")
        valid_config=False
    if 'stepper' not in config:
        error("'stepper' not set")
        valid_config=False
    if 'gearRatio' not in config:
        error("'gearRatio' not set")
        valid_config=False
    if 'v5' not in config['pins']:
        error("'pin_v5' not set")
        valid_config=False
    if 'stepperCoils' not in config['pins']:
        error("'pin_stepperCoils' not set")
        valid_config=False

    if not valid_config:
        help()
        sys.exit(3)

    if calculate:
        # we have been told something new, calculate from ideal
        config['delays']['calculated_ms']=calculate_step_delay_ms(config)

        # and force a calibration
        calibrate_iterations=DEFAULT_CALIBRATION_ITERATIONS

    # save state    
    save(config)

if __name__ == "__main__":
   make_config(sys.argv[1:])