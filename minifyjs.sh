#!/bin/bash

type uglifyjs2 >/dev/null 2>&1 || {
    echo >&2 "uglifyjs2 is not installed. Trying to install it with npm";
    type npm >/dev/null 2>&1 || {
        echo >&2 "npm is not installed. Trying to install it.";
        curl -L https://npmjs.org/install.sh | sh;
    }
    npm install uglify-js -g;
}
type uglifyjs2 >/dev/null 2>&1 || { echo >&2 "Failed to install uglifyjs2. Aborting."; exit 1; }

source_files=(
    'static/js/angular-queue.js'
    'static/js/http-interceptor.js'
    'static/js/app.js'
    'static/js/directives.js'
    'static/js/filters.js'
    'static/js/services.js'
    'static/js/controllers/mainController.js'
    'static/js/controllers/aboutController.js'
    'static/js/controllers/setupController.js'
    'static/js/controllers/logController.js'
    'static/js/controllers/checksController.js'
    'static/js/controllers/descriptionController.js'
    'static/js/controllers/metadataController.js'
    'static/js/controllers/reviewWebFontsController.js'
    'static/js/controllers/reviewGlyphInspectorController.js'
    'static/js/controllers/summaryController.js'
    'static/js/controllers/testsController.js'
    'static/js/controllers/reposController.js'
)

source_files_arg=$(IFS=" ";echo "${source_files[*]}")
echo "Minifying sources..."
echo "uglifyjs2 $source_files_arg --output static/js/all.min.js --source-map static/js/all.js.map --stats true"
echo ""

uglifyjs2 $source_files_arg --output static/js/all.min.js --source-map static/js/all.js.map --stats true
