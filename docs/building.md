# Building the Tracker

NOTE I am not affiliated with Amazon.  Any links I provide are just to help you out by providing exmaple hardware!

## How does it work?

The first thing is to understand how the stepper works.  Actually, the first thing is to decide what stepper to use.  I selected the 28BYJ-48 stepper motor with ULN2003 driver board.  Once the parts arrived I dove in trying to understand how it works.

There are tutorials and data sheets. And they are almost right.  But they ultimately don't quite get you there.  Here are a few I was referencing:

* [28BYJ-48 Data Sheet](https://components101.com/motors/28byj-48-stepper-motor)
* [Raspberry Pi Stepper Motor Control with L293D / ULN2003A](https://tutorials-raspberrypi.com/how-to-control-a-stepper-motor-with-raspberry-pi-and-l293d-uln2003a/)
* [Adafruit's Raspberry Pi Lesson 10. Stepper Motors](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-10-stepper-motors/overview)

What these give you is parts of the info but not everything.  And for reasons I cannot fathom the Raspberry Pi tutorial does not plug the stepper straight into the drive board!  I tinkered around and firgured out how to do it and here's the key things I learned.  Please keep in mind I haven't touched a Raspberry Pi since I setup OctoPi for my 3D printer 5 years ago, so I know almost literally nothing..

This model of stepper motor has 5 wires.  The colors are important, NOT the order they may be in the wiring harness.  Red is power, the others correspond to a coil by color.  There are 4 coils.  To move the motor you turn the coils on in a specific pattern.  There are several possible patterns but the recommended pattern uses 1/2 steps for this stepper.  Do that.  It's more steps in a sequence but you're writing code.  If it's just slightly more complex and RECOMMENDED who cares?

The wires from the stepper are connected on the side of the driver board with a clip for the stepper.  On the other side you hook up GPIO from the Pi.  The GPIO will will turn the coil ON.  This is important to note, as the data sheet indicates the sequence by which coil is held to ground and is therefore on.  So "0" on the data sheet is "1" in your program.

And don't forget power!  You can turn on the coil GPIO all you want, but without power turned on it does nothing.  Well, it still may do nothing if you wire it wrong, but that's a different problem!

Finally the question of speed.  This is controlled only by the delay between steps.  There's a HUGE gotya on this one:  each step will take a different amount of time.  Meaning it is not an accurate system.  But we can compensate for that.

Now for some math.  We are driving some gears that push a threaded rod.  We need to know how fast that rod will move.  The stepper has a motor in it and the data sheet gives how many degrees it moves per step. BUT it also has a gear reduction inside the motor.  So the stepper shaft moves on rotation based on that reduction.  The 28BYJ-48 stride angle is listed as "5.625°/64".  This means each step is 5.625° and the gear reduction is 64:1.  So one rotation is (360/5.625*64) = 4096 steps (using the recommended half step sequence).  This means to get our gears to turn at a specific rate we can simply put the right delay between steps.  But not really.  As noted, it isn't accurate.

To compensate for timing inacuraces in either the Pi or in the stepper I spent a good bit of time trying out things.  It's very easy to get a system setup that oscillates and gets worse over time.  The best pattern I found was to do a short snapshot of the expected vs actual time observed over a known number of steps and adjust the delay based on what was observed.  It won't be 100% accurate but we're talking 100's of ms over the course of half an hour, something like 0.025% drift.  Unless you're taking 30 minute exposures you won't notice it!  By the way, you won't take 30 minute exposures.  At 300mm I probably will try only 30 seconds. But that's better than the 2 seconds untracked by a LOT!

We have a stepper, and it's pretty accurate.  We just need to know what gears we're turning and the rod it's pushing so we know the delay for the stepper and the distance to put the rod from the pivot.  This model will let you pick these values if you have something different to work with.  

Key values to know:
* how many threads per mm for your rod
* how far center of rod is from the pivot point

I went with things from other models I saw around the interwebs and what I could get in my local hardware store:

* 1/4 inch threaded rod, 20 threads per inch
* rod 200mm from the hinge, because of print bed size

The radius (r) is 200mm.. And there are 0.7874 threads per mm (aka 20 threads per inch).  The circumference of the circle your rod travels is 2πr = 400π = 1256.6370mm.

The earth roughly rotates 360° / 24 hours, or 0.25° / minute.  Put another way, every minute the earth rotates 1 / 1440 % of the circumference of your circle.  That means every minute the rod needs to travel 0.8726mm.  (**NOTE** it isn't exactly / 24 hours, we will use the real value in the stepper code)

What we really need is the how many revolutions a nut on the rod must turn per minute.  Why the nut?  Our gear drives a nut, and one rotation is the distance of one thread along the rod.  And we pick one minute simply as a reasonable time scale to work with.  The rotation speed must be enough to move the rod 0.8726mm a minute.  Given 0.7874mm per thread that works out to 1.1082 rotations in a minute.

Now let's put that all together.  Our input date is:
- rod has 20 threads per inch (20 thread / 24.5 mm)
- radius of circle is 200 mm

Therefore we calculate the rotation required of the nut on the threaded rod per minute is:

(400π/1440) / (20/25.4) = 1.1082 revolutions per minute

Many barn door trackers work on a 1/4" rod at 290mm radius, which works out to 1 rotation per minute.  My motorized prototype did this just fine and the stepper could go faster.  This is a very doable number!  Let's get into building...

## Parts

Ok, explainations..

The tracker opens slowly on a hinge.  It's driven by your gears moving the threaded rod.  There are bearings at the hinge to help it be very smooth and the bolt just holds the bearings in the right place.  You attach the tracker to a tripod.  This should be sturdy.  Many tripods in the US have 3/8" bolts.  Mine has a 1/4" bolt.  You attach the camera on a separate camera mount.  I recommend a ball mount as the adjustment screws will not get in the way.  Again, in the US it's either 3/8" or 1/4".  Use the biggest you can for stability!

A note on camera mounting.  This model mounts it on the side of the tracker.  This provides more flexibility for getting shots.  If you mount it on the top it's likely you'll be limited since the ball mount won't allow enough movement to point at zenith.  I don't provide an option for a top mount because of this limitation.

If you are not using a 28BYJ-48 stepper motor you'll need ot adjust other parameters.  I won't get into these here.  And they're likely to be hard coded in the initial model anyway.  Sorry about that!

Buy the hardware first so you can measure things!

Make sure your hinge bolt is long enough.  You want the tracker to be around 4 inches (~100mm) wide.  If it's too long it's easy to cut it shorter with a hack saw.  It's really hard to make it longer..

If you don't have mini files yet do yourself a favor and get some.  They make cleanup much easier.  And if you get a set without handles just print some and heat press the file into the plastic!  I have a set similar to this [carbon steel 6 piece-set](https://amazon.com/dp/B07KH8BG1F/).

Hardware I used that is default for the model:
- 2 ea: 608-ZZ bearings (common for skateboards)
    - smooth hinge action
- 1 ea: 5/16" x 5" hex full thread bolt
    - holds bearings to the top plate of tracker
- 5 ea: 1/4" washer
    - 2 for the threaded rod attachment to the top plate
    - 2 for the hinge, optional
    - 1 _maybe_ as a spacer under the rod gear
- 1 ea: 5/16" nut
    - secure the bolt for the bearings
- 1 ea: 3/8" threaded rod
    - secure a camera mount
    - NOTE a bolt will work but limits flexibility
- 2 ea: 3/8" washer
    - for camera mount rod
- 3 ea: 3/8" nut
    - for camera mount rod
- 1 ea: 1/4"-20 x 20" threaded rod (20 thread / inch)
    - the rod you'll bend
- 2 ea: 1/4"-20 nut
    - to hold rod to the top plate
- 2 ea: 1/4" lock washer (optional)
    - to hold rod to the top plate
- 2 ea: 1/4"-20 cap nut (optional)
    - since you'll probably cut the threaded rod, provides smooth ends
- 1 ea: M4-0.7 x 8mm set screw
    - set screw to hold small gear to stepper
- 1 ea: ball head tripod mount
    - for attaching the camera to the tracker
    - do not get one with long adjustment rods!
    - Example: [Neewer Professional 35MM Low-Profile Ball Head 360 Degree Rotatable Tripod Head](https://amazon.com/gp/product/B08FB2Q5RC)
- 1 ea: 28BYJ-48 stepper motor
    - motor that does the work
- 1 ea: ULN2003 driver board
    - controls the motor based on GPIO signal
- 1 ea: Raspberry Pi of your choice
    - runs code that sends GPIO signal
- 6 ea: F/F jumper wire
    - wire the Pi to the driver board
- 1 ea: 5V power supply for Raspberry Pi
    - power supply for Pi (and through the Pi, the driver board + stepper)
    - I use the [Anker PowerCord II 20000](https://amazon.com/gp/product/B01LQ81QR0) I have already...


3D printed part list:
- 1 ea: 10 tooth stepper gear
- 1 ea: 43 tooth rod gear
- 1 ea: tracker top and bottom
- 1 ea: ULN2003 case and lid
- 1 ea: Raspberry Pi cases

Also included are 3D prints to test hardware and gears.  Use them!
- 1 ea: hardware test
- 1 ea: gear test

### TEST models

- File: [tracker.scad](src/scad/tracker.scad)
- Parts: **TEST: Hardware**, **TEST: Gears**
- STL: [TEST-hardware.stl](src/stl/TEST-hardware.stl), [TEST-gears.stl](src/stl/TEST-gears.stl)

This contains two test.  One is a block that you can test the bearing and **all** threaded hardware.  The other you verify placement of gears.  The gear placement model is techincally optional but I liked testing the gears on a quick print (30 minutes) before firing up the full tracker print (15 housr).

Please use these before you print the full model!  This will let you know if you need to tune any parameters for final print, including gear placement.

The "TEST: Hardware" model is very busy.  What you're testing and the params to tweak:
- Bearing = try pressing your bearing into the model.  It's better to break the test than the real model!
    - `bearing_diameter`
    - `bearing_height`
- EZ-Finder Mount = if you have a finder, see if it fits on here
    - nothing to tweak, it's hard coded.. you can glue something to the flat surface
- Visual Finder = just for reference, you don't do anything with this but look through without aid
    - nothing to tweak
- Camera Bolt = test your camera bolt goes into this as desired
    - `camera_bolt_diameter`
- Tripod = verify tripod bolt fits
    - `tripod_bolt_diameter`
- Hinge Bolt = test the hinge bolt
    - `hinge_bolt_diameter`
- Rod, Top = make sure the rod fits as desired
    - `rod_diameter`
- Rod, Bottom = the curve should be OK for the model, but you can verify with this
    - `rod_diameter`
    - `rod_T`

![TEST Hardware](images/test-hardware.png)



### GEAR: Stepper

- File: [tracker.scad](src/scad/tracker.scad)
- Part: **GEAR: Stepper**
- STL: [gear-stepper.stl](src/stl/gear-stepper.stl)

Only thing you might tweak is the set screw diameter.  I do recommend a set screw as the shaft doesn't have any threads to bite into the stepper gear.  The set screw will ensure alignment of the gear is consistent.  And if you can, put in 2 set screws.  The ones I got were sold in a pack of 2.

- `gear10_set_screw_diameter` = diameter of your set screw hole

### GEAR: Rod

- File: [tracker.scad](src/scad/tracker.scad)
- Part: **GEAR: Rod**
- STL: [gear-rod.stl](src/stl/gear-rod.stl)

The defaults get you a 43 tooth gear that fits a 1/4" rod.  I suggest only changing the dimensions for the nut.  You can play around with other factors but make sure you read up on terms!  I used this for reference [Gear Nomenclature](https://en.wikiversity.org/wiki/Gears#/media/File:Gearnomenclature.jpg).

- `gear43_nut_width` = width of the nut
- `gear43_nut_height` = height of the nut

### TRACKER Top and Bottom

- File: [tracker.scad](src/scad/tracker.scad)
- - Parts: **Tracker Top**, **Tracker Bottom**
STL: [tracker-top.stl](src/stl/tracker-top.stl), [tracker-bottom.stl](src/stl/tracker-bottom.stl)

The important bits are the size of your print bed.  I assume a pretty big print bed, sorry.  Maybe you can provide a PR for splitting it?  I didn't want any weak points.

You need to make sure your bolt will fit through the bearing!  The model does not care...  See the TEST: Hardware section for parameters to tweak.  In addition you may want to adjust the width and length of the tracker.  This can be done with:

- `tracker_radius` = how far away the center of the rod is from the hinge
- `hinge_length` = how wide the hinge is, probably a bit shorter than your bolt length to allow for washers and nut

### ULN2003 Case

- File: [tracker.scad](src/scad/tracker.scad)
- Parts: **ULN2003: Case**, **ULN2003: Lid**
- STL: [ULN2003-case.stl](src/stl/ULN2003-case.stl), [ULN2003-lid.stl](src/stl/ULN2003-lid.stl)

Shouldn't need any editing.  This is a simple case with a lid held by friction.  It has slots in the side for wires.  Mount to the tracker as you want.. glue, velcro, weld, whatever.

### Raspberry Pi Case

Not included.  Print what you like.  Attach to tracker.  Examples:

- [Raspberry Pi Pico Case](https://www.thingiverse.com/thing:4733137)
- [Raspberry Pi 3 (B/B+), Pi 2 B, and Pi 1 B+ case with VESA mounts and more](https://www.thingiverse.com/thing:922740)
- [Raspberry Pi 4B Case](https://www.thingiverse.com/thing:3793664)


## Print Settings

This is up to you.  It depends on your printer, how you can remove supports, etc.  What I did:

- Printer: LulzBot TAZ 5
- Nozzle: 0.5mm (stock is 0.35mm)
- Material: PolyLite PLA, True Black
- Layer Height: 0.38mm
- Infill: 40%
- Slicer: Cura LulzBot Edition, version 3.6.0 
- Supports: Custom

I used the [SUPPORT-bearing.stl](src/stl/SUPPORT-bearing.stl) to only support the bearing holes.  All other holes print fine for me, verified with the [TEST-hardware.stl](src/stl/TEST-hardware.stl).

**NOTE** it is much quicker to disable automatic slicing while moving around large parts:
1. Settings -> Configure settings visibility...
1. "General" section
1. Uncheck "Slice automatically"
1. Close

In order to use custom support in Cura:

1. Add [TRACKER-bottom.stl](src/stl/TRACKER-bottom.stl)
2. Add [SUPPORT-bearing.stl](src/stl/SUPPORT-bearing.stl)
3. Select the SUPPORT-bearing part
4. On the right, select "Custom" for "Print Setup".
5. On the left, select "Per Model Settings" (must be in "Custom" for this to be enabled)
6. Choose "Mesh Type" of "Print as support"
7. Use "Multiply Object" to add 1 more support
8. Move and scale as needed to fill the bearing areas

![Tracker with Custom Support in Cura](images/cura-with-custom-support.PNG)

## Print Order

I feel it's important to know what to print in what order so you can test and tune for the final product.  See the [TEST models](#TESTmodels) second for tweaking parameters.  I highly **highly** recommend this order.  This is also the order of parts in Customizer..

1. Print "TEST: Hardware".
2. Verify all hardware works.  See [TEST models](#test-models).
3. If adjustments are needed, make adjustments and go back 2 steps.
4. Print "GEAR: Stepper" and "GEAR: Rod".
5. Print "TEST: Gears".
6. Verify gears fit on tester.  See [TEST models](#test-models).
7. If adjustments are needed, make adjustments and go back 2 steps.
9. Print "TRACKER: Top" and "TRACKER: Bottom".
10. [Assemble!](#assembly)


