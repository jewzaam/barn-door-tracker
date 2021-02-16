from machine import Pin, Timer
import utime as time
led = Pin(25, Pin.OUT)

def blink(timer):
    led.toggle()

t=Timer()
try:
    t.init(mode=Timer.ONE_SHOT, period=5000, callback=blink)
    time.sleep(1000)
finally:
    led.off()
    t.deinit()
