from machine import Pin
import time

# simple script to test that you're communicated to the Pico.. blinks the on-board LED

pin_led = Pin(25, Pin.OUT)

try:
    while True:
        pin_led.toggle()
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    pin_led.off()