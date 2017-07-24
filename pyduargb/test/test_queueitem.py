from __future__ import print_function, absolute_import
import pytest

from ..animationqueue.queueitem import QueueItem

def test_queueitem():
    qi = QueueItem({}, 10)
    assert qi.get_animation() == {}
    assert qi.get_runlevel() == 10
    assert qi.get_sticky() == False
    assert qi.get_allow_lower_runlevel() == False

def test_allow_lower_run_level():
    qi = QueueItem({}, 10, False, True)
    qi2 = QueueItem({}, 5, False, True)
    assert qi.check_queue_permissions(qi2) == True

def test_higher_runlevel():
    qi = QueueItem({}, 10, False, False)
    qi2 = QueueItem({},15, False, False)
    assert qi.check_queue_permissions(qi2) == True

def test_lower_runlevel():
    qi = QueueItem({}, 10, False, False)
    qi2 = QueueItem({}, 5, False, False)
    assert qi.check_queue_permissions(qi2) == False

def test_equal_runlevel():
    qi = QueueItem({}, 10, False, False)
    qi2 = QueueItem({},10, False, False)
    assert qi.check_queue_permissions(qi2) == True
