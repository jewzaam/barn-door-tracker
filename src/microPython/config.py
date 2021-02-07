import os.path
import time, datetime
import yaml

CONFIG_FILENAME="stepper.yaml"

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
