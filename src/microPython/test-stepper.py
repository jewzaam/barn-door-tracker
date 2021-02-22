from machine import Pin, Timer
import utime as time
import select
import sys

# simple test that takes user input to set the step delay

sequence=[
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]

step=0

gpio_5v=18
gpio_coil=[28,27,26,22]
pin_5v=Pin(gpio_5v, Pin.OUT)
pins_coil=[]

def do_step(trigger):
    global step

    # very basic, do a step
    sequence_values=sequence[step]

    # update stepper coil outputs
    for i in range(0, len(sequence_values)):
        pins_coil[i].value(sequence_values[i])

    # setup next step
    step=(step+1)%len(sequence)

for g in gpio_coil:
    pins_coil.append(Pin(g, Pin.OUT))

delay_ms=5.0
timer=Timer()

try:
    
    pin_5v.on()

    while True:
        frequency=1000.0/delay_ms
        timer.init(freq=frequency, mode=Timer.PERIODIC, callback=do_step)
        print("Current step delay (ms): {}".format(delay_ms))
        try:
            delay_ms=eval(input("Next value (ms)? "))
        except:
            print("ERROR: unable to parse input, make sure it's a <float>")
finally:
    timer.deinit()
    pin_5v.off()
    for p in pins_coil:
        p.off()
