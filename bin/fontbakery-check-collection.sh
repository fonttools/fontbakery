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
rm $COLLECTION_FOLDER/*/*/*fontbakery.*

for f in $APACHE_FOLDERS $OFL_FOLDERS $UFL_FOLDERS
do
  LOGDIR=$RESULTS_FOLDER/$(basename $f)
  echo "$f" >> $RESULTS_FOLDER/all_fonts.txt

  if [ "$(ls -A $LOGDIR)" ]
  then
    echo "Skipping '$f'"
  else
    echo "Processing '$f'..."
    fontbakery check-ttf "$f*.ttf" --json --ghm --error
    mkdir -p $LOGDIR
    mv $f/CrossFamilyChecks.fontbakery.* $LOGDIR/ || echo "$f CrossFamilyChecks" >> $RESULTS_FOLDER/issues.txt
    for font in $f/*.ttf
    do
      mv $(basename $font).fontbakery.* $LOGDIR/ || echo "$font" >> $RESULTS_FOLDER/issues.txt
    done
  fi
done

cat $RESULTS_FOLDER/issues.txt

