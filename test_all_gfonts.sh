#!/bin/bash
FOLDERS=~/devel/github_google/fonts/*/*/

mkdir ./check_results/ -p
rm ./check_results/issues.txt -f

for f in $FOLDERS
do
  LOGDIR=./check_results/$(basename $f)
  echo $LOGDIR

  if [ "$(ls -A $LOGDIR)" ]
  then
    echo "Skipping '$LOGDIR'"
  else
    echo "Processing '$f'..."
    ./fontbakery-check-ttf.py "$f*.ttf" --json --ghm -vv
    mkdir -p $LOGDIR
    cp $f*fontbakery.* $LOGDIR || echo "$LOGDIR" >> ./check_results/issues.txt
  fi
done

cat ./check_results/issues.txt

