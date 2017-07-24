from __future__ import print_function, absolute_import

from ..animations.pulse import Pulse

def test_pulse_start():
    pulse = Pulse({'r': 255, 'g': 0, 'b': 0})
    pixels = pulse.animate_ns(0, 1000, 50)
    assert pixels[0].get_brightness() == 0

def test_pulse_middle():
    pulse = Pulse({'r': 255, 'g': 0, 'b': 0})
    pixels = pulse.animate_ns(500, 1000, 50)
    assert pixels[0].get_brightness() == 1

def test_pulse_end():
    pulse = Pulse({'r': 255, 'g': 0, 'b': 0})
    pixels = pulse.animate_ns(1000, 1000, 50)
    assert pixels[0].get_brightness() == 0

