# How to setup multiple Raspberry Pi's
Here we will go over the setup of multiple Raspberry Pi's.

## Master configuration
The master is the raspberry pi that controls the other raspberry pi's.
Technically their is no configuration required for the master raspberry pi.
The slave raspberry pi's will connect to it and be assigned a order depending on which
slave raspberry pi connects first.

If only one slave raspberry pi is going to be used and you are fine
with the default slave mode you can continue on with slave configuration.
But for more precise control we recommend setting up some paramaters in the master.

### Defining slaves on the master
Below is a example a master configuration
```
[master]
slavecount = 2

[slave0]
ip = 192.168.x.x  # ip of the slave
mode = contiue

[slave1]
ip = 192.168.x.x # ip of the second slave
mode = continue
```

In this example configuration 2 slaves are defined. `slave0` is the first slave.
and `slave1` is the second. The mode specified tells the master how to treat each
slave device. You can mix and match these modes for different lighting results.

#### Slave modes
##### Continue (default)
The `continue` mode treats the slave as if it was connected behind the master's
ledstrip. if you for example have 50 leds configured on your master and 50
on a slave device the master will act like it has 100 leds avaliable but send
50 of them to the slave.

When multiple slaves are configured in `continue` mode the order of the slave is
important. If the total leds in your setup is a 150 leds and each
raspberry pi has 50 leds, the first 50 will be displayed on your `master`
the next 50 on `slave0` and the final 50 on `slave1`

the `master` is always first. If you want a slave to be first you just need to make
that slave master instead.

##### Mirror
The `continue` mode acts as if the slave is mirrored. If the master has 50 leds
the master still acts like it has 50 leds but it will send a copy of the animation
data to the slave. This can be usefull if you want to light up 2 parts of your
room with the same animations.

### Slave configuration
the slave config is quite simple. Just setup a normal config and add the following
```
[master]
ip = 192.168.x.x (ip of master)
```
This tells the slave to try to contact master when it starts up.
It will keep trying to contact master but as long as it's not able to do so
the ledstrip will be turned off. The same is true if the ledstrip loses it's connection
to master.

##### Slave debugging
slaves can be cofigured to display a short pulse animation if a connection can't
be established or if connection is lost. This isn't default behaviour since
it can be annoying in normal day to day use. To enable this feature add
```
errorpulse = 1
```
to the master section of a slave. their is also the opposite
```
connectpulse = 1
```
That will display a short green pulse after a succesfull connection is established.
These features can be usefull in debugging.

### Some notes about slave behaviour
if PyDuaRGB is configured to act as a `slave` the default JSONRPC system is halted and can't be used.
A `slave` will make the connection to it's `master` this connection will remain open. A slave will try reconnect
if it loses connection to it's `master`.
