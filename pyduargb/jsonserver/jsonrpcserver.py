from __future__ import print_function, absolute_import, unicode_literals
from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher


from ..animations import pulse
from ..animationqueue import animationqueue, queueitem

@dispatcher.add_method
def add_pulse(color):
    animation = pulse.Pulse(color)
    qi = queueitem.QueueItem(1000, animation, 10, True, True)
    animationqueue.AnimationQueue().add_queueitem(qi)
    return True

#@dispatcher.add_method
#def list_animations():
#    pass

@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')
