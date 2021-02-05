import time
import math
import sys, getopt
import yaml
import os.path

DEBUG = False
CONFIG_FILENAME="stepper.yaml"
DEFAULT_CALIBRATION_ITERATIONS=30
SIDEREAL_DAY_IN_MINUTES=86164100/60000.0 # sidereal day in ms converted to minutes: http://www.kylesconverter.com/time/days-(sidereal)-to-milliseconds

def error(msg):
    print("ERROR: {}".format(msg))

def help():
    print("TODO: help text")

def save(config):
    with open(CONFIG_FILENAME, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

def load():
    config={}
    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, 'r') as infile:
            config=yaml.load(infile, Loader=yaml.FullLoader)
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
    gear_ratio=config['gear_ratio']

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

def main(argv):
    global DEBUG

    config = load()

    try:
        opts, args = getopt.getopt(argv,"hdc:r:p:s:g:",["help","debug","calibrate=","radius=","pitch=","stepper=","gearratio=","pin_v5=","pin_coils="])
    except getopt.GetoptError:
        print("math.py --calibrate <seconds> --debug")
        sys.exit(1)

    calculate=False

    if 'pins' not in config:
        config['pins']={}

    valid_config=True

    for opt, arg in opts:
        if opt == "-h":
            help()
            sys.exit()
        elif opt in ("-d", "--debug"):
            DEBUG = True
        elif opt in ("-c", "--calibrate"):
            calibrate_seconds = arg
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
        elif opt in ("-g", "--gearratio"):
            if 'gear_ratio' not in config or config['gear_ratio'] != arg:
                if len(arg.split(":")) != 2:
                    error("invalid format for '{}'".format(opt))
                    valid_config=False
                else:
                    config['gear_ratio'] = str(arg)
                    calculate=True
        elif opt in ("--pin_v5"):
            config['pins']['v5'] = int(arg)
        elif opt in ("--pin_coils"):
            config['pins']['coils'] = []
            for coil in arg.split(","):
                config['pins']['coils'].append(int(coil))

    save(config)

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
    if 'gear_ratio' not in config:
        error("'gearratio' not set")
        valid_config=False
    if 'v5' not in config['pins']:
        error("'pin_v5' not set")
        valid_config=False
    if 'coils' not in config['pins']:
        error("'pin_coils' not set")
        valid_config=False

    if not valid_config:
        help()
        sys.exit(3)

    if calculate:
        # we have been told something new, calculate from ideal
        config['delay_ms']=calculate_step_delay_ms(config)
        save(config)

        # and force a calibration
        calibrate_iterations=DEFAULT_CALIBRATION_ITERATIONS
    


if __name__ == "__main__":
   main(sys.argv[1:])