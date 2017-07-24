from __future__ import print_function, absolute_import
import pytest

from ..animationqueue.queue import *
from ..animationqueue.queueitem import *

def test_empty_queue():
    q = Queue()
    qi = QueueItem({}, 10)
    assert q.add_queueitem(qi) == True
    Queue.destroy()

def test_higher_runlevel():
    q = Queue()
    qi = QueueItem({}, 10)
    qi2 = QueueItem({}, 15)
    q.add_queueitem(qi)
    assert q.add_queueitem(qi2) == True
    Queue.destroy()

def test_lower_runlevel():
    q = Queue()
    qi = QueueItem({}, 10)
    qi2 = QueueItem({}, 9)
    q.add_queueitem(qi)
    assert q.add_queueitem(qi2) == False
    Queue.destroy()

def test_lower_runlevel_with_allow_lower():
    q = Queue()
    qi = QueueItem({}, 10, False, True)
    qi2 = QueueItem({}, 9)
    q.add_queueitem(qi)
    assert q.add_queueitem(qi2) == True
    Queue.destroy()

def test_runlevel_with_three_items():
    q = Queue()
    qi = QueueItem({}, 10, False, False)
    qi2 = QueueItem({}, 15, False, False)
    qi3 = QueueItem({}, 10, False, False)
    q.add_queueitem(qi)
    q.add_queueitem(qi2)
    assert q.add_queueitem(qi3) == False
    Queue.destroy()

def test_sticky():
    q = Queue()
    qi = QueueItem({}, 10, True, False)
    q.add_queueitem(qi)
    assert q._should_item_stick() == True
    Queue.destroy()

def test_sticky_more_then_one_item():
    q = Queue()
    qi = QueueItem({}, 10, True, False)
    qi2 = QueueItem({}, 11, False, False)
    q.add_queueitem(qi)
    q.add_queueitem(qi2)
    assert q._should_item_stick() == False
    Queue.destroy()

