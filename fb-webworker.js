importScripts('https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js');

const EXCLUDE_CHECKS = [
  'com.google.fonts/check/fontbakery_version', // We download the latest each time
  'com.daltonmaag/check/ufo_required_fields',
  'com.daltonmaag/check/ufo_recommended_fields',
  'com.google.fonts/check/designspace_has_sources',
  'com.google.fonts/check/designspace_has_default_master',
  'com.google.fonts/check/designspace_has_consistent_glyphset',
  'com.google.fonts/check/designspace_has_consistent_codepoints',
  'com.google.fonts/check/shaping/regression',
  'com.google.fonts/check/shaping/forbidden',
  'com.google.fonts/check/shaping/collides',
  'com.google.fonts/check/fontv', // Requires a subprocess

];

/** Produce an absolute URL for a wheel
*
* @param {string} path: the wheel's relative URL
* @return {string}
*/
function reroot(path) {
  return self.location.href.replace('fb-webworker.js', path);
}

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  await pyodide.loadPackage('micropip');
  const micropip = pyodide.pyimport('micropip');
  await micropip.install('glyphsets', false, false);
  await micropip.install([
    'axisregistry',
    'setuptools',
    'lxml',
    'fontTools>=4.53.0',
    'opentypespec',
    'munkres',
    'mock',
    'requests',
    'beziers>=0.5.0',
    'dehinter',
    'beautifulsoup4',
    'fs',
    'jinja2',
    'gfsubsets',
    'gflanguages',
  ]);
  await micropip.install('ufo2ft', false, false, null, true);
  await micropip.install('fontbakery', false, false, null, true);
  await pyodide.runPythonAsync(`
    from pyodide.http import pyfetch
    response = await pyfetch("${reroot('fbwebapi.py')}")
    with open("fbwebapi.py", "wb") as f:
        f.write(await response.bytes())
  `);
  await pyodide.pyimport('fbwebapi');
}
const pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async (event) => {
  // make sure loading is done
  const {id, files, profile, loglevels, fulllists} = event.data;
  try {
    await pyodideReadyPromise;
  }
  catch (error) {
    self.postMessage({error: error.message, id});
    return;
  }
  self.postMessage({ready: true});
  self.profile = profile;
  if (id == 'justload') {
    return;
  }
  if (id == 'listchecks') {
    try {
      const checks = await self.pyodide.runPythonAsync(`
          from fbwebapi import dump_all_the_checks

          dump_all_the_checks()
      `);
      self.postMessage({checks: checks.toJs()});
    } catch (error) {
      self.postMessage({error: error.message});
    }
    return;
  }

  try {
    const version = await self.pyodide.runPythonAsync(`
        import fontbakery
        fontbakery.__version__
    `);
    self.postMessage({version: version});
  }
  catch (error) {
    self.postMessage({error: error.message});
    return;
  }
  const callback = (msg) => self.postMessage(msg.toJs());

  // Write the files
  const filenames = [];
  for (const [name, buffer] of Object.entries(files)) {
    pyodide.FS.writeFile(name, buffer);
    filenames.push(name);
  }

  self.filenames = filenames;
  self.callback = callback;
  self.loglevels = loglevels;
  self.fulllists = fulllists;
  self.exclude_checks = EXCLUDE_CHECKS;
  try {
    await self.pyodide.runPythonAsync(`
        from fbwebapi import run_fontbakery
        from js import filenames, callback, exclude_checks, profile, loglevels, fulllists

        run_fontbakery(filenames,
          profilename=profile,
          callback=callback,
          loglevels=loglevels,
          full_lists=fulllists,
          exclude_checks=exclude_checks
        )
    `);
    self.postMessage({done: true});
  } catch (error) {
    self.postMessage({error: error.message, id});
  }
};
