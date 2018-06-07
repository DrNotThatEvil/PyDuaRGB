# PyduaRGB: The python daemon for your ledstrip needs.
# Copyright (C) 2018 wilvin@wilv.in

# This program is free software: you can redistribute it and/or modify
# it under the terms of GNU Lesser General Public License version 3
# as published by the Free Software Foundation, Only version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
