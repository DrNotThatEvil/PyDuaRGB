from __future__ import print_function, absolute_import, unicode_literals

from .pulse import Pulse
from .jirate import Jirate
from .static import Static
from .fadein import Fadein
from .fadeout import Fadeout

ALL_ANIMATIONS = [
   Pulse,
   Jirate,
   Static,
   Fadein,
   Fadeout
]

ANIMATION_MAP = {
    'pulse': Pulse,
    'jirate': Jirate,
    'static': Static,
    'fadein': Fadein,
    'fadeout': Fadeout
}
