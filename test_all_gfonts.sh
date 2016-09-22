#!/bin/bash
FOLDERS=~/devel/github_google/fonts/*/*/

mkdir ./check_results/ -p
rm ./check_results/issues.txt -f
rm ./check_results/all_fonts.txt -f

for f in $FOLDERS
do
  LOGDIR=./check_results/$(basename $f)
  echo "$f" >> ./check_results/all_fonts.txt

  if [ "$(ls -A $LOGDIR)" ]
  then
    echo "Skipping '$f'"
  else
    echo "Processing '$f'..."
    ./fontbakery-check-ttf.py "$f*.ttf" --json --ghm -vv
    mkdir -p $LOGDIR
    cp $f*fontbakery.json $LOGDIR/
    cp $f*.md $LOGDIR/ || echo "$f" >> ./check_results/issues.txt
  fi
done

cat ./check_results/issues.txt

