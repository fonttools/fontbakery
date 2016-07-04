#!/bin/bash
FOLDERS=~/devel/github_google/fonts/*/*/
for f in $FOLDERS
do
  JSON_LOG=./check_results/$(basename $f).json

  if [ -f $JSON_LOG ]
  then
    echo "$JSON_LOG found. Skipping."
  else
    echo "Processing '$f'..."
    ./fontbakery-check-ttf.py "$f/*.ttf" --ghm -vv
    #mv ./fontbakery-check-results.json ./check_results/$(basename $f).json || exit 1
  fi
done

