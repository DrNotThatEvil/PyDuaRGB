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
import pytest

from ..animationqueue.queueitem import QueueItem

def test_queueitem():
    qi = QueueItem(1000, {}, 10)
    assert qi.get_duration() == {}
    assert qi.get_animation() == {}
    assert qi.get_runlevel() == 10
    assert qi.get_sticky() == False
    assert qi.get_allow_lower_runlevel() == False

def test_allow_lower_run_level():
    qi = QueueItem(1000, {}, 10, False, True)
    qi2 = QueueItem({}, 5, False, True)
    assert qi.check_queue_permissions(qi2) == True

def test_higher_runlevel():
    qi = QueueItem(1000, {}, 10, False, False)
    qi2 = QueueItem({},15, False, False)
    assert qi.check_queue_permissions(qi2) == True

def test_lower_runlevel():
    qi = QueueItem(1000, {}, 10, False, False)
    qi2 = QueueItem(1000, {}, 5, False, False)
    assert qi.check_queue_permissions(qi2) == False

def test_equal_runlevel():
    qi = QueueItem(1000, {}, 10, False, False)
    qi2 = QueueItem(1000, {},10, False, False)
    assert qi.check_queue_permissions(qi2) == True
