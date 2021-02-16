import utime as time

def usleep(us,accuracy=0.99):
    usleep_from(time.ticks_us(),us,accuracy)

def usleep_from(start_tick,us,accuracy=0.99):
    diff = 0
    now = start_tick
    
    # loop until we're within the given accuracy or have gone over
    while diff < us and abs(diff/us)<accuracy:
        now = time.ticks_us()
        diff = time.ticks_diff(now,start_tick)

    return now

# utility function for sleep.. not used anymore but was a useful tool