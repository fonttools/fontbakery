#!/bin/bash
if [ "$1" ]; then
  COLLECTION_FOLDER=$1
else
  echo "usage: $0 <collection_folder>"
  exit 1
fi

APACHE_FOLDERS=$COLLECTION_FOLDER/apache/*
OFL_FOLDERS=$COLLECTION_FOLDER/ofl/*
UFL_FOLDERS=$COLLECTION_FOLDER/ufl/*
RESULTS_FOLDER=$COLLECTION_FOLDER/check_results

mkdir $RESULTS_FOLDER -p
rm $RESULTS_FOLDER/issues.txt -f
rm $RESULTS_FOLDER/all_fonts.txt -f
rm $COLLECTION_FOLDER/*/*/*fontbakery.*

for f in $APACHE_FOLDERS $OFL_FOLDERS $UFL_FOLDERS
do
  echo "$f" >> $RESULTS_FOLDER/all_fonts.txt
  echo "Processing '$f'..."
  LICENSE_DIR=$(basename "$(dirname $f)")
  REPORT=$RESULTS_FOLDER/$LICENSE_DIR/$(basename $f).json
  mkdir -p $(dirname $REPORT)
  fontbakery check-googlefonts --json $REPORT "$f/*.ttf"
done

cat $RESULTS_FOLDER/issues.txt

