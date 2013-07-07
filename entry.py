# Bakery entry script
import gevent.monkey
gevent.monkey.patch_all()

from socketio import socketio_manage

from bakery import create_app, init_app

app = create_app(app_name='bakery')
app.config['DEBUG'] = True
app.config.from_object('config')
app.config.from_pyfile('local.cfg', silent=True)
init_app(app)

import logging
LOG_FILENAME = 'data/run.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logging.info('Project start')

if __name__ == '__main__':
    import os
    from werkzeug.wsgi import SharedDataMiddleware
    app = SharedDataMiddleware(app, {
        '/': os.path.join(os.path.dirname(__file__), 'bakery', 'static')
        })
    from socketio.server import SocketIOServer
    SocketIOServer(('0.0.0.0', 5000), app,
        resource="socket.io", policy_server=False).serve_forever()
