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


from __future__ import print_function, absolute_import, unicode_literals

from .pulse import Pulse
from .random_pulse import RandomPulse
from .jirate import Jirate
from .static import Static
from .random_pixels import RandomPixels
from .fadein import Fadein
from .fadeout import Fadeout
from .racer import Racer
from .kitt import Kitt
from .binary_count import BinaryCount

ALL_ANIMATIONS = [
   Pulse,
   RandomPulse,
   Jirate,
   Static,
   RandomPixels,
   Fadein,
   Fadeout,
   Racer,
   Kitt,
   BinaryCount
]

ANIMATION_MAP = {
    'pulse': Pulse,
    'randompulse': RandomPulse,
    'randompixels': RandomPixels,
    'jirate': Jirate,
    'static': Static,
    'fadein': Fadein,
    'fadeout': Fadeout,
    'racer': Racer,
    'kitt': Kitt,
    'binarycount': BinaryCount
}
