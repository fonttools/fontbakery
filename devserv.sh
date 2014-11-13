#!/bin/bash

type python >/dev/null 2>&1 || {
    echo >&2 "python is not installed. Will try to use node's http-server.";
    type npm >/dev/null 2>&1 || {
        echo >&2 "npm is not installed. Trying to install it.";
        curl -L https://npmjs.org/install.sh | sh;
    }
    type http-server >/dev/null 2>&1 || {
        npm install http-server -g;
    }
    type http-server >/dev/null 2>&1 || {
        echo >&2 "Failed to install http-server. Aborting."; exit 1;
    }
}

if type python >/dev/null 2>&1;
    then
        python -m SimpleHTTPServer $@
    else
        http-server $@
fi
