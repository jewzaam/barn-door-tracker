# Background

## Untracked
When taking pictures of the stars you will get star trails if you don't compensage for the earth's movement.  In some cases this may be a desired shot!  It can be a pretty cool picture.  But for deep sky imaging it's not desired.

For example, here's a 30 second exposure of M42 (Orion Nebula) taken with a 300mm lens.

![M42 Untracked 30s](../images/M42-untracked-30s.jpg)

## Manual Tracker 
In order to get better shots of stars (astrophotography) I decided to build a barn door tracker.  My first version was an isometric version, meaning the threaded rod was straight and pivoted to keep in contact with the bottom board as it was rotated.  But it was also manual.  Humans are not good at spinning something consistently at such slow speeds without introducing additional vibrations!

![Tracker v1](../images/tracker-v1.jpg)

And it works!  Here's the same shot of M42 but for 150 seconds using the tracker.  It was processed a bit to make the nebula pop out more.  But the point is the lack of star trails.

![M42 Manual Tracking 150s](../images/M42-manual-tracking-150s.jpg)

You'll also notice that it isn't super clean.  And my experience doing this wasn't amazing.  Standing still for 2.5 minutes slowly cranking the tracker.. I got distracted, fell behind, added vibrations etc.

## Something Better...

I wanted to get a better shot and not have to manually manipulate this.  After a bit of research I settled on small stepper motor with controller driven by a Raspberry Pi I had laying around.  I have never used a stepper motor so it was a great excuse to learn even more new things.

