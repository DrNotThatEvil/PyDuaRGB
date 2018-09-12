# How the animation queue works
As stated earlier PyDuaRGB is designed with ledstrips in mind. The `AnimationQueue` is
a implementation designed to work with some the quirks of ledstrips and provides some usability enhancements
over a normal queue.

## Quriks of ledstrps
Many ledstrips require a constant stream of data to ensure that they display the proper color.
If you only send color data once the data changes the ledstrip can behave weirdly.

This is because noise on the wires connecting the ledstrip to the pi can sometimes
be interpreted by the ledstrip as color data. With the effect of turning some leds to a
different color or (as i experienced  myself) having your ledstrip turn on in the middle of the night.

### Ensuring a constant stream of data: the sticky flag
To prevent animations from quiting `QueueItem` objects have the `sticky` flag.
when `AnimationQueue` finishes a `QueueItem` it checks if the `sticky` flag is set
if so it will only remove the `QueueItem` from the queue if their is more then one `QueueItem` on
the `AnimationQueue`.

This behaviour ensures that the ledstrip has a constant stream of data.

## Queue access: Runlevels
PyDuaRGB gives applications easy access to your ledstrip, this is after all it's premise.
But sometimes you want to ensure specific behavior, runlevels give you more control to do so.

In a normal queue implementation every task would be accepted on the queue. If an app would push
an animation to your PyDuaRGB instance it would display it even in the middle of the night when your
trying to sleep. To ensure you have more control `AnimationQueue` does not behave in this way.

### Queue behavior
When a `QueueItem` is pushed to the `AnimationQueue` it does a check to see if it can be added.
If their is no item on the current queue it will always accept the `QueueItem`.
If the `AnimationQueue` is not empty it will peform a check to see if the new `QueueItem` should be
accepted.

The check compares the `QueueItem` to be added with the `QueueItem` at the top of the queue.
If the new `QueueItem` has a higher or equal `runlevel` value it will be accepted, else it will be rejected.
`QueueItem` objects also have a option to allow any runlevel to surpass them using the `allow_lower_runlevel` flag.

### How is this usefull?
Take the example mentioned above 'Ensuring the ledstrip to be off'.
We would push a `QueueItem` with the color black and a high runlevel to the `AnimationQueue`
this would prevent apps using lower runlevels from pushing their animations to the ledstrip. As soon as you want your ledstrip to resume normal operation you would push a `QueueItem` with a higher `runlevel` then the previous one
and set it's `allow_lower_runlevel` flag to true. This ensures that the new `QueueItem` can be added but
also ensures that apps (using lower runlevels) can push animations once again.

## Design considerations
### Decide runlevels
When designing your app decide how important the animations coming from your app are.
Are they of LOW, MODERATE or HIGH importance? Using this decide what runlevels you find appropriate to use for your animations. Keep in mind that users
might want to mute your apps animations (by pushing animations with higher runlevels) give them the ability to do so.

### Keep the queue tidy
When you push animations to the queue previous animations are pop'ed from the queue.
If your app pushes notifications for example it's your apps responsibility  to restore the previously playing animation. You can do this by getting
the current animation using the JSONRPC method `API_CALL` saving it locally and pushing it to the queue again
after pushing your animation. That way the previous animation will play again after your animation.
