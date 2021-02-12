from machine import Pin, Timer
import utime as time
led = Pin(25, Pin.OUT)

blink_count=25

def blink(timer):
    global blink_count
    led.toggle()
    blink_count-=1
    print(blink_count)
    if blink_count<=0:
        timer.deinit()

t=Timer()
try:
    t.init(freq=1, mode=Timer.PERIODIC, period=0, callback=blink)
    time.sleep(1000)
finally:
    led.off()
    t.deinit()
