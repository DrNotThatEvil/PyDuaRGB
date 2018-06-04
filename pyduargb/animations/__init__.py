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
