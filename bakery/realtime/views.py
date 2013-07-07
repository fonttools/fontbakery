import logging

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from flask import (Blueprint, request)

realtime = Blueprint('realtime', __name__)

# The socket.io namespace
class BuildNamespace(BaseNamespace):
    def on_subscribe(self, project_id):
        pass

@realtime.route("/socket.io/<path:path>")
def run_socketio(path):
    socketio_manage(request.environ, {
        '/build': BuildNamespace,
        })