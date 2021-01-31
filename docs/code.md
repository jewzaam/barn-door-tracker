# Code

File: [stepper.py](../src/python/stepper.py)

You need to set the right pins based on how you've wired you Pi and the inputs for your hardware.  I don't have CLI arguments, so just crack open the code and edit parameters at the top of the file.  The default values are those used for the explaination in this document.

- `debug`: set to `True` if you want to see data printed on startup and every calibration
- `tracker_radius_mm`: the radius of the tracker
- `tracker_threads_per_mm`: how may threads per mm
- `gpio_power`: the GPIO pin that provides power to the drive controller
- `gpio_coils`: the GPIO pins _in order_ that are wired to the stepper coils: orange, yellow, pink, blue

That's it!  Everything else is done in code assuming you didn't deviate from the 28BYJ-48 stepper, ULN2003 drive controller, and external gear ratio of 43:10.

If you change the stepper, controller, or gear ratio there are more things you need to fiddle with.  The variable names should make things obvious, or comments will help.  When not clear, do some math and check the debug output to see if things line up with expectations.

## Installation

Copy your version of [stepper.py](../src/python/stepper.py) to the Raspberry Pi.  I assume it's in the `/home/pi/` directory.

## Automatic Start

You can search the web but what I did was add a crontab entry as root:

```shell
sudo crontab -e
```

And put the following at the end of the crontab:

```shell
@reboot python /home/pi/stepper.py
```
## Calibration

You do not have to do calibartion!  This is done automatically.  This section just summarizes the techinque and what to look for in the debug output if interested in how close to expected values things are when you run the code.

This script is simple but not trivial.. it does a dynamic calibration of the delay between steps.  It measure actual time vs expected time and adjusts the delay between steps.  It's done the whole time the program runs.  The key is to do a pretty short sampling.  If you do a long sample it ends up oscillating, swingging wider over time from ideal.  The way it is setup right now works very well to dial in to a reasonable margin of error and keep it there.

Note the error is higher on startup because it is based on the ideal data sheet numbers.  In my testing, _within 10 seconds_ the error rate stars hovering around `0.01%` with a few bips higher but overall very good.

To see exactly what is going on you can run with `debug` set to `True` and watch the console output.  Interesting values:

- `momentary_error` = percentage that actual time is off expected time over the last `step_count` steps
- `total_error` = the overall total error percentage

---
Back to the [Index](00-index.md)!