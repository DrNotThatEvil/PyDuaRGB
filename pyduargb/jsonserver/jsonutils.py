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

from ..animations import ANIMATION_MAP


def get_animation_class(name):
    if(name not in ANIMATION_MAP):
        return False

    return ANIMATION_MAP[name]


def get_required_params(obj):
    if obj.__init__.__defaults__ is None:
        return []

    defaults = list(reversed(obj.__init__.__defaults__))
    var_names = list(obj.__init__.__code__.co_varnames)
    var_names.pop(0)
    return [x for i, x in enumerate(reversed(var_names))
            if not (-len(defaults) <= i < len(defaults))]
