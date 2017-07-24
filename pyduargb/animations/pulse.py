from __future__ import print_function, absolute_import

from pyduargb.pixel import Pixel

class Pulse(object):
   
    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        # animation pulses a single color 
        # animation takes 0.40 of the duration to fade in and out. The time in the middle 
        # the ledstrip will take to display the color statically

        percent = i / duration
        step = (1 / 0.40)
        brightness = 0 

        brightness = 0.0 + (percent * step)

        if (percent > 0.40 and percent < 0.60):
            brightness = 1.0
        
        if (percent >= 0.60):
            brightness = 0.0 + ((percent-0.60) * step) 
            brightness = 1.0 - brightness

        if (percent == 1.0):
            brightness = 0

        return [Pixel(self.color, brightness) for count in range(ledcount)]

