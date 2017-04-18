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
  db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
  r.connect(db_host, 28015).repl()
  db = r.db('fontbakery')
#  db.table('cached_stats').index_create('familyname').run();
  fonts_prod = list(db.table('cached_stats').order_by(index='familyname').filter({"commit": "prod"}).run())
  return render_template("dashboard.html", prod=fonts_prod)


@app.route('/testsuite/')
def testsuite_overview():
  if 1:  #try:
    db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
    r.connect(db_host, 28015).repl()
    db = r.db('fontbakery')
    targets = db.table('check_results').filter({"commit": "prod"}).run()
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

    fonts_prod = list(db.table('check_results').filter({"commit": "prod", "familyname": familyname}).run())
    fonts_dev = list(db.table('check_results').filter({"HEAD": True, "familyname": familyname}).run())

    family_prod = db.table('cached_stats').filter({"commit": "prod", "familyname": familyname}).run().next()
    family_dev = []
    try:
      family_dev = db.table('cached_stats').filter({"HEAD": True, "familyname": familyname}).run().next()
    except:
      pass

    chart_data = [["Results", "Occurrences"]]
    delta = {}
    for k in family_prod['summary']:
      if k != "Total":
        chart_data.append([k, family_prod['summary'][k]])
        if family_dev != [] and k in family_dev['summary']:
          delta[k] = (family_dev['summary'][k] - family_prod['summary'][k])

    for f in fonts_dev + fonts_prod:
      if '-' in f['fontname'] and '.ttf' in f['fontname']:
        f['stylename'] = f['fontname'].split('-')[1].split('.ttf')[0]
      else:
        f['stylename'] = "{} (bad name)".format(f['fontname'])

    # I think that the rearrangement of data below could be avoided by crafting a smarter database schema...
    fonts = []
    for p in fonts_prod:
      for d in fonts_dev:
        if d['stylename'] == p['stylename']:
          fonts.append([p, d])

    return render_template("family_details.html",
                           delta=delta,
                           fonts=fonts,
                           familyname=familyname,
                           chart_data=json.dumps(chart_data),
                           giturl=family_prod['giturl'])
#  except:
#    return render_template("under_deployment.html")


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
