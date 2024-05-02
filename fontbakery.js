
const SORT_RESULT = {
  'FAIL': 'aa',
  'WARN': 'bb',
  'INFO': 'cc',
  'ERROR': 'dd',
  'PASS': 'ee',
  'SKIP': 'zz',
};

const NOWASM = (s) => `
This check cannot be run in the web environment. This is because ${s}.
The web version of fontbakery is not a full replacement for the Python
version, and we recommend that you install fontbakery and check your
fonts locally to ensure that all checks are run.`;
const CANT_COMPILE = (s) => NOWASM(`the ${s} library cannot be compiled for WASM`);
const NEEDS_NETWORK = NOWASM("it needs access to the network");
const BABELFONT =  NOWASM('the check requires a library (babelfont) with a Rust dependency');
const EXCUSES = {
  // Needs dependencies
  'com.adobe.fonts/check/freetype_rasterizer': CANT_COMPILE('Freetype'),
  'com.google.fonts/check/ots': CANT_COMPILE('OpenType Sanitizer'),
  'com.google.fonts/check/alt_caron:googlefonts': BABELFONT,
  'com.google.fonts/check/alt_caron': BABELFONT,
  'com.google.fonts/check/arabic_high_hamza': BABELFONT,
  'com.google.fonts/check/arabic_spacing_symbols': BABELFONT,
  'com.google.fonts/check/legacy_accents:googlefonts': BABELFONT,
  // Needs network
  'com.google.fonts/check/vendor_id': NEEDS_NETWORK,
  'com.google.fonts/check/fontdata_namecheck': NEEDS_NETWORK,
  'com.google.fonts/check/vertical_metrics_regressions': NEEDS_NETWORK,
  'com.google.fonts/check/metadata/includes_production_subsets': NEEDS_NETWORK,
  'com.google.fonts/check/metadata/designer_profiles': NEEDS_NETWORK,
  'com.google.fonts/check/description/broken_links': NEEDS_NETWORK,
  'com.google.fonts/check/metadata/broken_links': NEEDS_NETWORK,
  'com.google.fonts/check/version_bump': NEEDS_NETWORK,
  'com.google.fonts/check/production_glyphs_similarity': NEEDS_NETWORK,
  // Shaping checks
  'com.google.fonts/check/render_own_name': CANT_COMPILE('Freetype'),
  'com.google.fonts/check/dotted_circle': CANT_COMPILE('cffsubr [required by ufo2ft]'),
  'com.google.fonts/check/metadata/can_render_samples': CANT_COMPILE('Harfbuzz'),
  'com.google.fonts/check/slant_direction': CANT_COMPILE('Harfbuzz'),
  'com.google.fonts/check/glyphsets/shape_languages': CANT_COMPILE('Harfbuzz'),

  // Other checks
  'com.google.fonts/check/metadata/family_directory_name': NOWASM('there are no directories in the WASM environment'),
};
const fbWorker = new Worker('./fb-webworker.js');

/** Show that we have loaded the Python code, allow baking */
function showLoaded() {
  $('#loading').hide();
  $('#test').show();
  $('#listcheckscontainer').show();
}

/** Update the progress bar
 *
 * @param {Map} progress - Progress message
*/
function showProgress(progress) {
  const pct = progress.get('progress');
  $('#progress .progress-bar').css({'width': `${pct}%`});
  if (pct == 100) {
    $('#progress').hide();
  }
  for (const result of Object.keys(SORT_RESULT)) {
    const count = progress.get(result);
    if (count) {
      $(`#${result}-count`).html(count);
    }
  }
}

/** Start again
*/
function reset() {
  $('#normalresults').show();
  $('#listchecks').hide();
  $('#startModal').show();
}


/** Display an error modal
 *
 * Used to display Python errors.
 * @param {string} msg - HTML error message
*/
function showError(msg) {
  $('#errorModal').show();
  $('#errorText').html(msg);
}

/** Record a result and add it to the output pills
 *
 * Used to display Python errors.
 * @param {Map} data - All the stuff
*/
function showResult(data) {
  console.log("Got a result", data)
  $('#startModal').hide();
  const tabid = $('#v-pills-tab').children().length;
  const result = data.get('result');
  const checkid = data.get('key');
  let thispill = $(`#v-pills-tab button[data-checkid="${checkid}"]`);
  // console.log("Adding result for ",checkid)
  if (thispill.length == 0) {
    // Add a new pill
    thispill = $(`
        <button
          class="nav-link bg-${result}"
          id="v-pills-${tabid}-tab"
          data-toggle="pill"
          data-target="#v-pills-${tabid}"
          data-sortorder="${SORT_RESULT[result]}"
          type="button"
          role="tab"
          data-checkid=${data.get('key')}
          aria-controls="v-pills-${tabid}">${data.get('description')}</button>
      `);
    // Add a header if we need one
    $('#v-pills-tab').append(thispill);
    if ($(`#v-pills-tab button[data-sortorder=${SORT_RESULT[result]}`).length == 1) {
      var header_sort = SORT_RESULT[result].substring(0, 1);
      $('#v-pills-tab').append($(`
        <button class="nav-link disabled header-${result}" data-sortorder="${header_sort}">
        </div>
      `))
    }
  }
  let thistab = $(`#v-pills-tabContent div[data-checkid="${checkid}"]`);
  if (thistab.length == 0) {
    thistab = $(`
      <div
        class="tab-pane fade"
        data-sortorder="${SORT_RESULT[result]}"
        id="v-pills-${tabid}"
        role="tabpanel"
        aria-labelledby="v-pills-${tabid}-tab"
        data-checkid=${data.get('key')}
      >
        <h4>${data.get('description')}</h4>
        <p class="text-muted">${data.get('key')}</p>
        <div class="rationale">
        ${ CmarkGFM.convert((data.get('rationale')||'').replace(/^ +/gm, '')) }
        </div>
        <ul class="results">
        </ul>
      </div>
      `);
    $('#v-pills-tabContent').append(thistab);
    
  }
  // Update pill / tab results with worst result
  if (SORT_RESULT[result] < thispill.data('sortorder')) {
    thispill.removeClass(function(index, className) {
      return (className.match(/(^|\s)bg-\S+/g) || []).join(' ');
    });
    thispill.addClass('bg-' + result);
    thispill.data('sortorder', SORT_RESULT[result]);
    thistab.data('sortorder', SORT_RESULT[result]);
  }

  if (result == 'ERROR' && EXCUSES[checkid]) {
    thistab.find('ul.results').append(`<li>${EXCUSES[checkid]}</li>`);
  } else {
    for (log of data.get('logs')) {
      let where = 'ul.results';
      if (data.has('filename')) {
        const filename = data.get('filename');
        where = `ul.results li ul[data-filename='${filename}']`;
        if (thistab.find(where).length == 0) {
          thistab.find('ul.results').append(`<li>
            <b>${filename}</b>
            <ul data-filename="${filename}">
            </ul>
          </li>`);
        }
      }
      thistab.find(where).append($(`
            <li>
              <span
                class="bg-${log.get('status')} font-weight-bold">
                ${log.get('status')}
              </span>:
              <div>${CmarkGFM.convert(log.get('message').get('message'))}</div>
            </li>
          `));
    }
  }
  // Sort the tabs based on result
  tinysort('div#v-pills-tab>button', {'data': 'sortorder'});
  tinysort('div#v-pills-tabContent>div', {'data': 'sortorder'});
}

/* Add a profile from the profiles list */
PROFILES = {
  'opentype': 'OpenType (standards compliance)',
  'universal': 'Universal (community best practices)',
  'googlefonts': 'Google Fonts',
  'adobefonts': 'Adobe Fonts',
  'fontbureau': 'Font Bureau',
  'typenetwork': 'Type Network',
  'fontwerk': 'Fontwerk',
  'microsoft': 'Microsoft',
};

function addProfile(profilename, col) {
  const checked = profilename == 'universal' ? 'checked': '';
  const widget = $(`
    <div class="form-check">
        <input class="form-check-input" type="radio" name="flexRadioDefault" id="profile-${profilename}" ${checked}>
        <label class="form-check-label" for="profile-${profilename}">
           ${PROFILES[profilename]}
        </label>
    </div>
  `);
  $(`#profiles .row #col${col}`).append(widget);
}

/**
 * Display all the checks
 *
 * @param {Map} checks: Metadata about the checks
 **/
function listChecks(checks) {
  $('#startModal').hide();
  $('#listchecks').show();
  $('#normalresults').hide();
  for (const [id, check] of checks) {
    const card=$(`
      <div class="card my-4">
        <div class="card-header">
          <code>${id}</code>
        </div>
      <div class="card-body">
        <a name="${id}"><h2> ${check.get('description')} </h2></a>
        ${CmarkGFM.convert(check.get('rationale')||'')}
        <table class="table">
          <tr>
            <th>Sections</th>
            <td class="sections"></td>
          </tr>
          <tr>
            <th>Profiles</th>
            <td class="profiles"></td>
          </tr>
        </table>
      </div>
    </div>
    `);
    if (check.has('severity')) {
      card.find('.table').prepend(
          $(`<tr><th>Severity</th><td>${check.get('severity')}</td></tr>`)
      );
    }
    if (check.has('proposal')) {
      card.find('.table').prepend(
          $(`<a href="${check.get('proposal')}">More information</a>`)
      );
    }
    for (const section of check.get('sections')) {
      card.find('.sections').append(
          $(`<span class="badge rounded-pill bg-primary"> ${section} </span>`)
      );
    }
    for (const profile of check.get('profiles')) {
      card.find('.profiles').append(
          $(`<span class="badge rounded-pill bg-primary"> ${profile} </span>`)
      );
    }
    $('#checks').append(card);
  }
}

fbWorker.onmessage = (event) => {
  if ('checks' in event.data) {
    listChecks(event.data.checks);
    return;
  }
  if ('ready' in event.data) {
    showLoaded();
    return;
  }
  if ('version' in event.data) {
    $("#fb-version").html(event.data.version);
  }

  if ('checks' in event.data) {
    console.log(event.data);
    return;
  }
  if ('done' in event.data) {
    $('#v-pills-tab button:first-child').tab('show');
    return;
  }
  if ('error' in event.data) {
    showError(event.data.error);
    // otherwise data is a Map
  } else if (event.data.has('progress')) {
    showProgress(event.data);
  } else {
    showResult(event.data);
  }
};

Dropzone.autoDiscover = false;
files = {};

$(function() {
  Dropzone.options.dropzone = {
    url: 'https://127.0.0.1/', // This doesn't matter
    maxFilesize: 10, // Mb
    accept: function(file, done) {
      const reader = new FileReader();
      reader.addEventListener('loadend', function(event) {
        files[file.name] = new Uint8Array(event.target.result);
      });
      reader.readAsArrayBuffer(file);
    },
  };
  Dropzone.discover();
  $('[data-toggle="tooltip"]').tooltip();
  Object.keys(PROFILES).forEach( (profilename, ix) => {
    addProfile(profilename, ix % 2);
  });
  $('#startModal').show();
  $('#test').click(function() {
    const profile = $('#profiles .form-check-input:checked')[0].id.replace('profile-', '');
    const fulllists = $('#full-lists').is(':checked');
    const loglevels = $('#loglevels').val();
    fbWorker.postMessage({profile, files, loglevels, fulllists});
  });
  $('#listchecksbtn').click(function() {
    fbWorker.postMessage({id: 'listchecks'});
  });
  $('.leftarrow').click(reset);
  fbWorker.postMessage({id: 'justload'});
});
