# How the animation queue works
As stated earlier PyDuaRGB is designed with ledstrips in mind. The `AnimationQueue` is
a implementation desgined to work with some the quirks of ledstrips and provides some useability enhancements
over a normal queue.

## Quriks of ledstrps
Many ledstrips require a constant stream of data to ensure that they display the proper color.
If you only send color data once the data changes the ledstrip can behave weirdly.

This is because noise on the wires connecting the ledstrip to the pi can sometimes
be interpreted by the ledstrip as color data. With the effect of turning some leds to a
different color or (as i experinced myself) having your ledstrip turn on in the middle of the night.

### Ensuring a constant stream of data: the sticky flag
To prevent animations from quiting `QueueItem` objects have the `sticky` flag.
when `AnimationQueue` finishes a `QueueItem` it checks if the `sticky` flag is set
if so it will only remove the `QueueItem` from the queue if their is more then one `QueueItem` on
the `Queue`.

This behaviour ensures that the ledstrip has a constant stream of data.

## Runlevels
Ledstrips are great but somtimes you do not want to be disturbed.. 
