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

To prevent this `QueueItem` objects have the `sticky` flag. When `AnimationQueue` ...

TODO CONTINUE HERE.
