from flask import Flask, render_template
import rethinkdb as r
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
  if 1: #try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    static = os.environ.get("STATIC_FILES")
    r.connect(db_host, 28015).repl()
    db = r.db('fontbakery')
    fonts = db.table('cached_stats').filter({"HEAD": True}).run()
    return render_template("dashboard.html", fonts=fonts, static=static)
#  except:
#    return render_template("under_deployment.html")


@app.route('/testsuite')
def testsuite_overview():
  if 1:  #try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    r.connect(db_host, 28015).repl()
    db = r.db('fontbakery')
    targets = db.table('check_results').filter({"HEAD": True}).run()
    families = []
    checks = {}
    num_targets = 0
    for target in targets:
      num_targets +=1
      if target['familyname'] not in families:
        families.append(target['familyname'])

      for check in target['results']:
        desc = check['description']
        result = check['result']
        if desc not in checks.keys():
          checks[desc] = {'OK':0,
                          'Total': 0,
                          'ERROR': 0,
                          'WARNING': 0,
                          'SKIP': 0,
                          'INFO': 0}

        checks[desc][result] += 1
        checks[desc]['Total'] += 1

    return render_template("testsuite.html",
                           checks=checks,
                           num_targets=num_targets,
                           num_families=len(families)
                          )
#  except:
#    return render_template("under_deployment.html")


@app.route('/details/<familyname>')
def family_details(familyname):
  try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    r.connect(db_host, 28015).repl()
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
