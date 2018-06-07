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
import os
import json
from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher

from .jsonutils import *
from ..config import config_system
from ..animationqueue import animationqueue
from ..animations import pulse
from ..animationqueue import animationqueue, queueitem


CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_PATH = os.path.realpath(os.path.join(CUR_PATH, '..', '..'))


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
    configsys = config_system.ConfigSystem()
    return {"led_count": configsys.get_option('main', 'leds').get_value()}


# Queue manipulation section
@dispatcher.add_method
def add_queueitem(duration, animation, runlevel, sticky, allow_lower_runlevel):
    animation_obj = get_animation_class(animation["name"]).from_json(animation)
    qi = queueitem.QueueItem(
        duration,
        animation_obj,
        runlevel,
        sticky,
        allow_lower_runlevel
    )
    animationqueue.AnimationQueue().add_queueitem(qi)
    return qi.to_json()


@Request.application
def application(request):
    allowed = config_system.ConfigSystem().get_option(
        'jsonrpc', 'allow'
    ).get_value()
    if allowed != '0.0.0.0' and allowed != request.remote_addr:
        return Response('access denied',
                        status=403, mimetype='text/plain')

    if request.method != 'POST':
        return Response('pyduargb led control', mimetype='text/plain')

    data = json.loads(request.data.decode("utf-8"))
    # NOTE: Removed apitoken. jsonrpc is only safe for local network anyway
    # due to http making the apitoken useless.

    response = JSONRPCResponseManager.handle(
        json.dumps(data), dispatcher)
    return Response(response.json, mimetype='application/json')
