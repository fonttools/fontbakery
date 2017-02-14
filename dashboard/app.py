from flask import Flask
app = Flask(__name__)

@app.route('/')
def dashboard():
    return "Here we'll rneder the dashboard main page later."

if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
