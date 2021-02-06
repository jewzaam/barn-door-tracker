from machine import Pin
import time

pin_power = Pin(28, Pin.OUT)
pin_led = Pin(25, Pin.OUT)

gp_input=[28,27,26,22,21,16]

gp_active=-1

pins_input = []

try:
    # create a Pin for each input
    for gp in gp_input:
        p = Pin(gp, Pin.IN, Pin.PULL_DOWN)
        pins_input.append(p)

    # turn on LED (so we know it's working)
    pin_led.on()
    # and power to the switch
    pin_power.on()

    # loop and check each input
    while True:
        for i in range(0, len(gp_input)):
            pin = pins_input[i]
            gp = gp_input[i]

            print("Checking {}".format(gp))

            if pin.value() and gp_active!=gp:
                print("Pin active: {}".format(gp))
                gp_active=gp

            if not pin.value() and gp_active==gp:
                print("Pin inactive: {}".format(gp))
                gp_active=-1

        # for easier debugging with printed output
        print("")
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    pin_power.off()
    pin_led.off()