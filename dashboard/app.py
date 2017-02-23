from flask import Flask, render_template
import rethinkdb as r

app = Flask(__name__)

@app.route('/')
def dashboard():
  try:
    r.connect('db', 28015).repl()
    db = r.db('fontbakery')
    fonts = db.table('cached_stats').filter({"HEAD": True}).run()
    return render_template("dashboard.html", fonts=fonts)
  except:
    return render_template("under_deployment.html")


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
