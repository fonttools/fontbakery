from bakery.app import app

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(port=5001)
