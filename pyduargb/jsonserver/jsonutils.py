from __future__ import print_function, absolute_import

from ..animations import ANIMATION_MAP


def get_animation_class(name):
    if(name not in ANIMATION_MAP):
        return False

    return ANIMATION_MAP[name]
