#!/bin/bash
if [ "$1" ]; then
  COLLECTION_FOLDER=$1
else
  echo "usage: $0 <collection_folder>"
  exit 1
fi

APACHE_FOLDERS=$COLLECTION_FOLDER/apache/*/
OFL_FOLDERS=$COLLECTION_FOLDER/ofl/*/
UFL_FOLDERS=$COLLECTION_FOLDER/ufl/*/
RESULTS_FOLDER=$COLLECTION_FOLDER/check_results/

mkdir $RESULTS_FOLDER -p
rm $RESULTS_FOLDER/issues.txt -f
rm $RESULTS_FOLDER/all_fonts.txt -f

for f in $APACHE_FOLDERS $OFL_FOLDERS $UFL_FOLDERS
do
  LOGDIR=$RESULTS_FOLDER/$(basename $f)
  echo "$f" >> $RESULTS_FOLDER/all_fonts.txt

  if [ "$(ls -A $LOGDIR)" ]
  then
    echo "Skipping '$f'"
  else
    echo "Processing '$f'..."
    ./fontbakery-check-ttf.py "$f*.ttf" --json --ghm -vv
    mkdir -p $LOGDIR
    cp $f*fontbakery.json $LOGDIR/
    cp $f*.md $LOGDIR/ || echo "$f" >> $RESULTS_FOLDER/issues.txt
  fi
done

cat $RESULTS_FOLDER/issues.txt

