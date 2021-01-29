# WORK IN PROGRESS

Some of this is accurate, some of it is being written ahead of code or model changes.  If you're seeing this header it's not 100% ready!


# Background

## Untracked
When taking pictures of the stars you will get star trails if you don't compensage for the earth's movement.  In some cases this may be a desired shot!  It can be a pretty cool picture.  But for deep sky imaging it's not desired.

For example, here's a 30 second exposure of M42 (Orion Nebula) taken with a 300mm lens.

![M42 Untracked 30s](images/M42-untracked-30s.jpg)

## Manual Tracker 
In order to get better shots of stars (astrophotography) I decided to build a barn door tracker.  My first version was an isometric version, meaning the threaded rod was straight and pivoted to keep in contact with the bottom board as it was rotated.  But it was also manual.  Humans are not good at spinning something consistently at such slow speeds without introducing additional vibrations!

![Tracker v1](images/tracker-v1.jpg)

And it works!  Here's the same shot of M42 but for 150 seconds using the tracker.  It was processed a bit to make the nebula pop out more.  But the point is the lack of star trails.

![M42 Manual Tracking 150s](images/M42-manual-tracking-150s.jpg)

You'll also notice that it isn't super clean.  And my experience doing this wasn't amazing.  Standing still for 2.5 minutes slowly cranking the tracker.. I got distracted, fell behind, added vibrations etc.

## Something Better...

I wanted to get a better shot and not have to manually manipulate this.  After a bit of research I settled on small stepper motor with controller driven by a Raspberry Pi I had laying around.  I have never used a stepper motor so it was a great excuse to learn even more new things.

# Building the Tracker

## How does it work?

The first thing is to understand how the stepper works.  Actually, the first thing is to decide what stepper to use.  I selected the 28BYJ-48 stepper motor with ULN2003 driver board.  Once the parts arrived I dove in trying to understand how it works.

There are tutorials and data sheets. And they are almost right.  But they ultimately don't quite get you there.  Here are a few I was referencing:

* [28BYJ-48 Data Sheet](https://components101.com/motors/28byj-48-stepper-motor)
* [Raspberry Pi Stepper Motor Control with L293D / ULN2003A](https://tutorials-raspberrypi.com/how-to-control-a-stepper-motor-with-raspberry-pi-and-l293d-uln2003a/)
* [Adafruit's Raspberry Pi Lesson 10. Stepper Motors](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-10-stepper-motors/overview)

What these give you is parts of the info but not everything.  And for reasons I cannot fathom the Raspberry Pi tutorial does not plug the stepper straight into the drive board!  I ultimately firgured out how to do it and here's the key things I learned.  Please keep in mind I haven't touched a Raspberry Pi since I setup OctoPi for my 3D printer 5 years ago, so I know almost literally nothing..

This model of stepper motor has 5 wires.  The colors are important NOT the order they may be in the wiring harness.  Red is power, the others correspond to a coil.  There are 4 coils.  To move the motor you turn the coils on in a specific pattern.  There are several possible patterns but the recommended pattern uses 1/2 steps.  Do that.  It's more steps in a sequence but you're writing code.  If it's just slightly more complex and RECOMMENDED who cares?

The wires from the stepper are connected on the side of the driver board with a clip for the stepper.  On the other side you hook up GPIO from the Pi.  The GPIO will will turn the coil ON.  This is an important distinction as the data sheet indicates the sequence by which coil is held to ground and is therefore on.  So "0" on the data sheet is "1" in your program.

And don't forget power!  You can turn on the coil GPIO all you want, but without power turned on it does nothing.  Well, it still may do nothing if you wire it wrong, but that's a different problem!

Finally the question of speed.  This is controlled only by the delay between steps.  There's a HUGE gotya on this one:  each step will take a different amount of time.  Meaning it is not an accurate system.  But we can compensate for that.

Now for some math.  We are driving some gears that push a threaded rod.  We need to know how fast that rod will move.  The stepper has a motor in it and the data sheet gives how many degrees it moves per step. BUT it also has a gear reduction  inside the motor.  So the stepper shaft moves on rotation based on that reduction.  The 28BYJ-48 stride angle is listed as "5.625°/64".  This means each step is 5.625° and the gear reduction is 64:1.  So one rotation is (360/5.625*64) = 4096 steps (using the recommended half step sequence).  This means to get our gears to turn at a specific rate we can simply put the right delay between steps.  But not really.  It's not accurate.

To compensate for timing inacuraces in either the Pi or in the stepper I spent a good bit of time trying out things.  It's very easy to get a system setup that oscillates and gets worse over time.  The best pattern I found was to do a short snapshot of the expected vs actual time taken for the number of steps and adjust the delay based on what was observed.  It won't be 100% accurate but we're talking 100's of ms over the course of half an hour, something like 0.025% drift.  Unless you're taking 30 minute exposures you won't notice it!

We have a stepper, and it's pretty accurate.  We just need to know what gears we're turning and the rod it's pushing so we know the delay for the stepper and the distance to put the rod from the pivot.  This model will let you pick these values if you have something different to work with.  I went with things from other models I saw around the interwebs and what I could get in my local hardware store:

* 1/4 inch threaded rod, 20 threads per inch
* 1 rotation of rod's gear per minute

Key values to know:
* how many threads per mm for your rod
* how far center of rod is from the pivot point

Let's say the rod is 200mm from the pivot point.  This is a comfortable size for me to 3D print.  This is the radius (r). And there are 0.7874 threads per mm (aka 20 threads per inch).  The circumference of the circle your rod travels is 2πr = 400π = 1256.6370mm.

The earth roughly rotates 360° / 24 hours, or 0.25° / minute.  Put another way, every minute the earth rotates 1 / 1440 % of the circumference of your circle.  That means every minute the rod needs to travel 0.8726mm.

What we really need is the how many revolutions a nut on the rod must turn per minute.  Why a nut?  Each revolution travels the distance of one thread.  And we pick one minute simply as a reasonable time scale to work with.  The rotation speed must be enough to move the rod 0.8726mm a minute.  Given 0.7874mm per thread that works out to 1.1082 rotations in a minute.

Now let's base that on the hard data.
- rod has 20 threads per inch (20 thread / 24.5 mm)
- radius of circle is 200 mm

Rotation per minute is:

(400π/1440) / (20/25.4) = 1.1082 revolutions per minute

This is a very doable number!  Let's get into building...

## Parts

Ok, explainations..

The tracker opens slowly on a hinge.  It's driven by your gears moving the threaded rod.  There are bearings at the hinge to help it be very smooth and the bolt just holds the bearings in the right place.  You attach the tracker to a tripod.  This should be sturdy.  Many tripods in the US have 3/8" bolts.  Mine has a 1/4" bolt.  You attach the camera on a separate camera mount.  I recommend a ball mount as the adjustment screws will not get in the way.  Again, in the US it's either 3/8" or 1/4".  Use the biggest you can for stability!

A note on camera mounting.  This model mounts it on the side of the tracker.  This provides more flexibility for getting shots.  If you mount it on the top it's likely you'll be limited since the ball mount won't allow enough movement to point at zenith.  I don't provide an option for a top mount because of this limitation.

If you are not using a 28BYJ-48 stepper motor you'll need ot adjust other parameters.  I won't get into these here.  And they're likely to be hard coded in the initial model anyway.  Sorry about that!

Buy the hardware first so you can measure things!

Make sure your bolt is long enough.  You want the tracker to be around 4 inches (~100mm) wide.  If it's too long it's easy to cut it shorter with a hack saw.  It's really hard to make it longer..

Hardware I used that is default for the model:
- 2 ea: 608-ZZ bearings (common for skateboards)
- 1 ea: 5/16" x 5" hex full thread bolt
- 1 ea: 5/16" nut
- 1 ea: 1/4"-20 x 20" threaded rod (20 thread / inch)
- 2 ea: 1/4"-20 nut
- 4 ea: 1/4" washer
- 2 ea: 1/4" lock washer
- 2 ea: 1/4"-20 cap nut
- 1 ea: 28BYJ-48 stepper motor
- 1 ea: ULN2003 driver board
- 1 ea: Raspberry Pi of your choice
- 6 ea: F/F jumper wire

3D printed part list:
- 1 ea: 10 tooth stepper gear
- 1 ea: 43 tooth rod gear
- 1 ea: tracker top and bottom
- 1 ea: ULN2003 case and lid
- 1 ea: Raspberry Pi cases

Store Bought Part List:

### 10 tooth stepper gear

I didn't create a model for this, I took one from [Barn Door tracker remix for 28byj-48 stepper](https://www.thingiverse.com/thing:2841827).  See file `astroBarnLittleGearMod2Screw.stl`.

### 43 tooth rod gear

File: [gear.scad](src/scad/gear.scad)

The defaults get you a 43 tooth gear that fits a 1/4" rod.  I suggest only changing the dimensions for the rod and the nut.  You can play around with other factors but make sure you read up on terms!  I used this for reference [Gear Nomenclature](https://en.wikiversity.org/wiki/Gears#/media/File:Gearnomenclature.jpg).

- shaft_diameter =  rod diameter
- nut_width = width of the nut
- nut_height = height of the nut

## tracker top and bottom

File: [tracker.scad](src/scad/tracker.scad)

The important bits are the size of your print bed.  I assume a pretty big print bed, sorry.  Maybe you can provide a PR for splitting it?  I didn't want any weak points.

You need to make sure your bolt will fit through the bearing!  The model does not care...

- tracker_radius = how far away the center of the rod is from the hinge
- hinge_diameter = how wide the bolt at the hinge is
- hinge_length = how wide the hinge is, probably a bit shorter than your bolt length to allow for washers and nut
- bearing_diameter = the hinge bearing outer diameter
- bearing_height = height of the bearing
- tripod_bolt_diameter = diameter of rod/bolt/whatever that attaches to the tripod
- camera_bolt_diameter = diameter of the rod/bolt/whatever that attaches to the camera
- rod_diameter = diameter of the threaded rod

You can use the `part` parameter to get just the model for the **"top"** or **"bottom"**.

## ULN2003 case and lid

File: [case-uln2003.scad](src/scad/case-uln2003.scad)

Shouldn't need any editing.  This is a simple case with a lid held by friction.  It has slots in the side for wires.  Mount to the tracker as you want.. glue, velcro, weld, whatever.

## Raspberry Pi case

Not included.  Print what you like.  Attach to tracker.

# Code

File: [stepper.py](src/python/stepper.py)

You need to set the right pins based on how you've wired you Pi and the inputs for your hardware.

- tracker_radius = how far away the center of the rod is from the hinge (same value from [tracker.scad](src/scad/tracker.scad))
- threads_per_mm = measure of how many threads per mm on the threaded rod
- stepper_gear_teeth = number of teeth on the gear attached to the stepper motor
- rod_gear_teeth = number of teeth on the gear attached to the threaded rod

NOTE this all assumes 28BYJ-48 stepper motor.  If you have a different stepper you need to look at the data sheet to identify:
- how many steps per rotation of the motor shaft
- how many coils need wired and how to wire it
- order to activate coils (sequence)

## Calibration

This script is simple but not trivial.. it does a dynamic calibration of the delay between steps.  It measure actual time vs expected time and adjusts the delay between steps.  It's done the whole time the program runs.  The key is to do a pretty short sampling.  If you do a long sample it ends up oscillating, swingging wider over time from ideal.  The way it is setup right now works very well to dial in to a reasonable margin of error (0.025% or so) and keep it there.

## Automatic Start

You can search the web but what I did was add a crontab entry as root:

```shell
sudo crontab -e
```

And put the following at the end of the crontab:

```shell
@reboot python /home/pi/stepper.py
```


# Assembly

