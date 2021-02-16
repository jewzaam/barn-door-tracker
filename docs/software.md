# Hardware & Software

I staretd out developing this for a Raspberry Pi 4b.  The code is still there (see [stepper.py](../src/python/stepper.py)) but I have moved on to the Raspberry Pi Pico which is very different.  This document assumes:

- You are using a Raspberry Pi Pico
- You are wiring it the same way documented here
- You can change the code if you use another device or wire it differently


## Accuracy

The current software uses timers for:
* stepper control
* input (irq)
* blinking led

Therefore it is very accurate.  Tuning the radius of the tracker dynamically shows a higher error % on shutdown (print to stdout) but this is momentary in reality because of the use of timers.  Best case is turning on the Pico and no touching any controls until termination.  On termination you get the percentage drift between actual and expected times.  In a 60 second test I got this output:

```shell
avg_actual_delay_ms: 4.94393
total_error_p: -0.01140833%
```

After 4 minutes:

```shell
avg_actual_delay_ms: 4.943915
total_error_p: 0.04760027%
```

After 11 minutes:

```shell
avg_actual_delay_ms: 4.941289
total_error_p: 0.04693866%
```

- `avg_actual_delay_ms` is average delay in ms for each step
- `total_error_p` is the error between actual and expected total times

As you can see, it's pretty close.  It does accumulate some error but it isn't much.  And errors are momentary.  The timer will stive for the configured frequency regardless of what has happened on previous executions.

This is done by having the interupts (timer or irq) set a boolean flag and return.  There's a main control loop that then takes those flags to perform the actions required.  This way the timer blocks as little as possible.  Keep in mind the execution time for a periodic timer (used for stepper control, button input, and led blinking) callback is not part of the timer's period.  Setting 4 coil states took about 250ms.  Having that inside the timer results in a 250ms longer delay than expected.  By moving it out to the main control loop and not part of the timer's interuupt it is executed while the timer is waiting to fire again.

## How Hot Does it Get?

You might worry on a hot summer night about the temperatures.  I was wondering myself!  So I did a very simple test of the temperatures of the Pico, drive controller, and stepper in my office.  They were all resting on my bamboo desk.  The Pico powered by a USB battery (same one I take out for pictures).  The office ambient temperature is 74F.  I am rounding the temperatures as this is only to give peace of mind, not to be a rigerous study of how these components heat up over time.  And the times are simply when I remembered to take the temperatures, not premeditated!

![Temperatures over Time](../images/temp-over-time.png)

---
Back to the [Index](00-index.md)!