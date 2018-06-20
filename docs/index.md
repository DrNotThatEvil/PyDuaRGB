# PyDuaRGB
The open source python ledstrip manager.

## What is PyDuaRGB?
PyDuaRGB is a python daemon to manage a ledstrip connected to a Raspberry Pi.
PyDuaRGB offers a JSONRPC api to control animations. It's ment as a interface between
your software/scripts and a ledstrip.

## Why was it created?
I wanted to create a system to notify me of emails using a ledstrip. While developing
this tool i realized that a simple way to interface with a ledstrip could be usefull
for more applications then an simple email notifier. So i started work to extend
the functionality of the existing system. This system ended up way to bloated
and I decided to rework the application to a simple interface that could be extended
by other apps and systems that version is PyDuaRGB.

### Features
This system was written from the ground up to be used with ledstrips. ledstrips are
quite simple in their implementation, but have some quirks that this system is designed to deal with.
This system is offers the following features:

* Designed for ledstrips
* Pretty neat animations (if i say so myself)
* Simple JSONRPC api so easy to implement in your apps!
* Control multiple ledstrips connected to multiple Raspberry Pi's all in sync!
* Completly Open Source LGPL Version 3

Upcomming freatures:
* Direct control api to drive the ledstrip directly so let your imagination flow!
* Works with multiple ledstrip types! See [Supported chips](./supported_chips.md)

## Installation instructions
For installation instructions please view our [Install guide](./Install_guide.md)
