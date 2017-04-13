from flask import Flask, render_template, send_from_directory
import rethinkdb as r
import json
import os

app = Flask(__name__, static_url_path='')


@app.route('/css/<path>/')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/js/<path>/')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/')
def dashboard():
  if 1: #try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    r.connect(db_host, 28015).repl()
    db = r.db('fontbakery')
    fonts = db.table('cached_stats').filter({"HEAD": True}).run()
    return render_template("dashboard.html", fonts=fonts)
#  except:
#    return render_template("under_deployment.html")


@app.route('/testsuite/')
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
                          'SKIP':0,
                          'HOTFIX': 0,
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


@app.route('/details/<familyname>/errorlog/')
def family_error_log(familyname):
  db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
  r.connect(db_host, 28015).repl()
  db = r.db('fontbakery')
  family = db.table('fb_log').filter({"familyname": familyname}).run()

  logs = list(family)

  return render_template("error_log.html",
                         logs=logs)


@app.route('/details/<familyname>/')
def family_details(familyname):
  if 1: #try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    r.connect(db_host, 28015).repl()
    db = r.db('fontbakery')
    family = db.table('cached_stats').filter({"HEAD": True, "familyname": familyname}).run()
    fonts = db.table('check_results').filter({"HEAD": True, "familyname": familyname}).run()

    the_family = family.next()
    chart_data = [["Results", "Occurrences"]]
    for k in the_family['summary']:
      if k != "Total":
        chart_data.append([k, the_family['summary'][k]])

    fonts = list(fonts)
    for f in fonts:
      if '-' in f['fontname'] and '.ttf' in f['fontname']:
        f['stylename'] = f['fontname'].split('-')[1].split('.ttf')[0]
      else:
        f['stylename'] = "{} (bad name)".format(f['fontname'])

    return render_template("family_details.html",
                           fonts=fonts,
                           familyname=familyname,
                           chart_data=json.dumps(chart_data),
                           giturl=the_family['giturl'])
#  except:
#    return render_template("under_deployment.html")


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
