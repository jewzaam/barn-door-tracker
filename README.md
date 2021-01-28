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

MORE TO COME.. started it but I'm tired so will pick it up later

The earth roughly rotates 360° / 24 hours.  For one rotation of the rod is ....