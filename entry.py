from bakery import create_app

if __name__ == '__main__':
    app = create_app(app_name='bakery')
    app.config['DEBUG'] = True
    app.config.from_object('config')
    app.config.from_pyfile('local.cfg', silent=True)
    app.run(port=5001)
