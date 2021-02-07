from machine import Pin, Timer
import utime as time
led = Pin(25, Pin.OUT)

def blink_fast(timer):
    start=time.ticks_ms()
    now=start
    while time.ticks_diff(now,start) < 5000.0:
        led.toggle()
        time.sleep_ms(250)
        now=time.ticks_ms()
    print("DONE: blink_fast")

Timer().init(mode=Timer.ONE_SHOT, period=0, callback=blink_fast)
