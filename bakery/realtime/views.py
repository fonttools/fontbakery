import logging

from socketio import socketio_manage
from socketio.namespace import BaseNamespace, GlobalNamespace
from socketio.mixins import RoomsMixin #, BroadcastMixin

from flask import (Blueprint, request)

realtime = Blueprint('realtime', __name__)

# The socket.io namespace
class Hello(BaseNamespace):

    def on_hello(self, data):
        print "hello", data
        self.emit('greetings', {'from': 'sockets'})


class BuildNamespace(BaseNamespace):

    # def logreader(self, project_id):

    #     pass

    # def on_subscribe(self, project_id):
    #     self.spawn(self.logreader, project_id)

    def on_start(self):
        self.emit('start', {'from': 'sockets'})

    def on_stop(self):
        self.emit('stop', {'from': 'sockets'})



@realtime.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {
        '': GlobalNamespace,
        '/hello': BuildNamespace,
        '/build': BuildNamespace,
        })