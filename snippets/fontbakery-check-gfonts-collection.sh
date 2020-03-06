#!/bin/bash
echo "This script expects to find font-families organized in the same directory structure as the Google Fonts git repo at https://github.com/google/fonts/"
echo "The collection_folder specified in the command-line must contain sub-directories with license names ('ofl', 'ufl' or 'apache') and familyname directories within those."

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

mkdir -p $RESULTS_FOLDER
rm -f $RESULTS_FOLDER/issues.txt
rm -f $RESULTS_FOLDER/all_fonts.txt
rm -f $COLLECTION_FOLDER/*/*/*fontbakery.json

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
