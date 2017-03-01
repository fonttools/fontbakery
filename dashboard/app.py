from flask import Flask, render_template
import rethinkdb as r
import json

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


@app.route('/details/<familyname>')
def family_details(familyname):
  try:
    r.connect('db', 28015).repl()
    db = r.db('fontbakery')
    family = db.table('cached_stats').filter({"HEAD": True, "familyname": familyname}).run()
    fonts = db.table('check_results').filter({"HEAD": True, "familyname": familyname}).run()

    summary = family.next()['summary']
    chart_data = [["Results", "Occurrences"]]
    for k in summary:
      if k != "Total":
        chart_data.append([k, summary[k]])

    fonts = list(fonts)
    for f in fonts:
      if '-' in f['fontname'] and '.ttf' in f['fontname']:
        f['stylename'] = f['fontname'].split('-')[1].split('.ttf')[0]
      else:
        f['stylename'] = "{} (bad name)".format(f['fontname'])

    return render_template("family_details.html",
                           fonts=fonts,
                           familyname=familyname,
                           chart_data=json.dumps(chart_data))
  except:
    return render_template("under_deployment.html")


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
