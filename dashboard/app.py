from flask import Flask, render_template
import rethinkdb as r

app = Flask(__name__)
r.connect('db', 28015).repl()

@app.route('/')
def dashboard():
  db = r.db('fontbakery')
  fonts = db.table('cached_stats').run()
  return render_template("dashboard.html", fonts=fonts)

if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
