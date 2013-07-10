import logging

from flask import Response
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from flask import (Blueprint, request)

realtime = Blueprint('realtime', __name__)

# The socket.io namespace
class HelloNamespace(BaseNamespace):

    def on_hello(self, data):
        print "hello", data
        self.emit('greetings', {'from': 'sockets'})

class BuildNamespace(BaseNamespace):

    def initialize(self):
        print("Socketio session started")

    # def logreader(self, project_id):

    #     pass

    # def on_subscribe(self, project_id):
    #     self.spawn(self.logreader, project_id)

    def on_start(self):
        self.emit('start', {})

    def on_stop(self):
        self.emit('stop', {})

    def on_hello(self, message):
        print(message)
        self.emit('ping', {})

    def recv_message(self, message):
        print ("PING!!!", message)


@realtime.route('/socket.io/<path:remaining>')
def socketio(remaining):
    socketio_manage(request.environ, {
        '/chat': HelloNamespace,
        '/build': BuildNamespace,
        }, request)
    return Response()
