from __future__ import print_function, absolute_import, unicode_literals

from .pulse import Pulse
from .jirate import Jirate

ALL_ANIMATIONS = [
   Pulse,
   Jirate
]

ANIMATION_MAP = {
    'pulse': Pulse,
    'jirate': Jirate
}
