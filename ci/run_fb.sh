#!/bin/sh
file_names=`curl -v -H "Authorization: token $GH_TOKEN" "https://api.github.com/repos/$TRAVIS_REPO_SLUG/pulls/$TRAVIS_PULL_REQUEST/files" | jq '.[] | .filename' | tr '\n' ' ' | tr '"' ' '`
fontbakery check-googlefonts $file_names -l FAIL -n
