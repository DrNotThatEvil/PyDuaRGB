from __future__ import print_function, absolute_import, unicode_literals
import os
from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher


from .jsonutils import *
from ..config import config_system
from ..animationqueue import animationqueue
from ..animations import pulse
from ..animationqueue import animationqueue, queueitem


CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_PATH = os.path.realpath(os.path.join(CUR_PATH, '..', '..'))
CONFIGSYS = config_system.ConfigSystem(os.path.join(MAIN_PATH, 'config.ini'))


# Queue Section
@dispatcher.add_method
def get_animation_queue():
    queue = animationqueue.AnimationQueue()
    return {"animationqueue": queue.get_json_queue()}

@dispatcher.add_method
def get_current_queueitem():
    queue = animationqueue.AnimationQueue()
    queueitems = queue.get_queue()
    if(len(queueitems) == 0):
        return {"current_item": None}

    return {"current_item": queueitems[0].to_json()}

# Config Section 
@dispatcher.add_method
def get_led_count():
    return {"led_count": CONFIGSYS.get_option('main', 'leds').get_value()}


# Queue manipulation section
@dispatcher.add_method
def add_queueitem(duration, animation, runlevel, sticky, allow_lower_runlevel):
    animation_obj = get_animation_class(animation["name"]).from_json(animation)
    qi = queueitem.QueueItem(duration, animation_obj, runlevel, sticky, allow_lower_runlevel)
    animationqueue.AnimationQueue().add_queueitem(qi)
    return qi.to_json()


@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]


@Request.application
def application(request):
    # Handle api token
    print(request)

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')
