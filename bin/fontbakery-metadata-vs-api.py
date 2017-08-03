#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import sys
import urllib
import urlparse
import json
from fontbakery.fonts_public_pb2 import FamilyProto
from google.protobuf import text_format

description = ("This script compares the info on local METADATA.pb files"
               " with data fetched from the Google Fonts Developer API.\n\n"
               " In order to use it you need to provide an API key.")
parser = argparse.ArgumentParser(description=description)
parser.add_argument('key', help='Key from Google Fonts Developer API')
parser.add_argument('repo',
                    help=('Directory tree that contains'
                          ' directories with METADATA.pb files.'))
parser.add_argument('--cache',
                    help=('Directory to store a copy'
                          ' of the files in the fonts developer API.'),
                    default="/tmp/fontbakery-compare-git-api")
parser.add_argument('--verbose',
                    help='Print additional information',
                    action="store_true")
parser.add_argument('--ignore-copy-existing-ttf', action="store_true")
parser.add_argument('--autofix',
                    help='Apply automatic fixes to files.',
                    action="store_true")
parser.add_argument('--api',
                    help='Domain string to use to request.',
                    default="fonts.googleapis.com")


def get_cache_font_path(cache_dir, fonturl):
    urlparts = urlparse.urlparse(fonturl)
    cache_dir = os.path.join(cache_dir,
                             urlparts.netloc,
                             os.path.dirname(urlparts.path).strip('/'))
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fontname = os.path.basename(fonturl)
    return os.path.join(cache_dir, fontname)

def getVariantName(item):
    if item.style == "normal" and item.weight == 400:
        return "regular"

    name = ""
    if item.weight != 400:
        name = str(item.weight)

    if item.style != "normal":
        name += item.style

    return name


API_URL = 'https://www.googleapis.com/webfonts/v1/webfonts?key={}'
def main():
    args = parser.parse_args()
    response = urllib.urlopen(API_URL.format(args.key))
    try:
        webfontList = json.loads(response.read())['items']
        webfontListFamilyNames = [item['family'] for item in webfontList]
    except (ValueError, KeyError):
        sys.exit("Unable to load and parse"
                 " list of families from Google Web Fonts API.")

    for dirpath, dirnames, filenames in os.walk(args.repo):
        metadata_path = os.path.join(dirpath, 'METADATA.pb')
        if not os.path.exists(metadata_path):
            continue

        metadata = FamilyProto()
        text_data = open(metadata_path, "rb").read()
        text_format.Merge(text_data, metadata)
        try:
            family = metadata.name
        except KeyError:
            print(('ERROR: "{}" does not contain'
                   ' familyname info.').format(metadata_path),
                  file=sys.stderr)
            continue

        try:
            index = webfontListFamilyNames.index(family)
            webfontsItem = webfontList[index]
        except ValueError:
            print(('ERROR: Family "{}" could not be found'
                   ' in Google Web Fonts API.').format(family))
            continue

        webfontVariants = []
        log_messages = []
        for variant, fonturl in webfontsItem['files'].items():
            cache_font_path = get_cache_font_path(args.cache, fonturl)
            webfontVariants.append(variant)

            if args.ignore_copy_existing_ttf and os.path.exists(cache_font_path):
                continue

            with open(cache_font_path, 'w') as fp:
                found = False
                for font in metadata.fonts:
                    if getVariantName(font) == variant:
                        found = True
                        if args.verbose:
                            print('Downloading "{}"'
                                  ' as "{}"'.format(fonturl,
                                                    font.filename))

                        #Saving:
                        fp.write(urllib.urlopen(fonturl).read())

                        #Symlinking:
                        src = cache_font_path
                        dst_dir = os.path.dirname(cache_font_path)
                        dst = os.path.join(dst_dir, font.filename)
                        if not os.path.exists(dst):
                            os.symlink(src, dst)
                if not found:
                    print(("ERROR: Google Fonts API references"
                           " a '{}' variant which is not declared"
                           " on local '{}'.").format(variant,
                                                     metadata_path))

        for subset in webfontsItem['subsets']:
            if subset == "menu":
                # note about Google Web Fonts:
                # Menu subsets are no longer generated offline.
                continue

            if subset not in metadata.subsets:
                print(('ERROR: "{}" '
                       'lacks subset "{}" in git.').format(family, subset),
                      file=sys.stderr)
            else:
                if args.verbose:
                    print(('OK: "{}" '
                           'subset "{}" in sync.').format(family, subset))

        for subset in metadata.subsets:
            if subset != "menu" and subset not in webfontsItem['subsets']:
                print(('ERROR: "{}" '
                       'lacks subset "{}" in API.').format(family, subset),
                      file=sys.stderr)

        if metadata.category.lower() != webfontsItem['category']:
            print(('ERROR: "{}" category "{}" in git'
                   ' does not match category "{}"'
                   ' in API.').format(family,
                                      metadata.category,
                                      webfontsItem['category']))
        else:
            if args.verbose:
                print(('OK: "{}" '
                       'category "{}" in sync.').format(family,
                                                        metadata.category))


        for variant in webfontVariants:
            try:
                idx = [getVariantName(f) for f in metadata.fonts].index(variant)
                repoFileName = metadata.fonts[idx].filename

                fonturl = webfontsItem['files'][variant]
                fontpath = get_cache_font_path(args.cache, fonturl)

                import hashlib
                google_md5 = hashlib.md5(open(fontpath, 'rb').read()).hexdigest()
                data = open(os.path.join(dirpath, repoFileName), 'rb').read()
                repo_md5 = hashlib.md5(data).hexdigest()

                if repo_md5 == google_md5:
                    log_messages.append([variant,
                                         'OK',
                                         '"{}" in sync'.format(repoFileName)])
                else:
                    log_messages.append([variant,
                                         'ERROR',
                                         ('"{}" checksum mismatch, file'
                                          ' in API does not match file'
                                          ' in git.').format(repoFileName)])

            except ValueError:
                log_messages.append([variant,
                                     'ERROR',
                                     ('"{}" available in API but'
                                      ' not in git.').format(font.filename)])

        for font in metadata.fonts:
            variant = getVariantName(font)
            try:
                webfontVariants.index(variant)
            except ValueError:
                log_messages.append([variant,
                                     'ERROR',
                                     ('"{}" available in git but'
                                      ' not in API.').format(font.filename)])

        # Sort all the messages by their respective
        # metadataFileName and print them:
        for message in sorted(log_messages, key=lambda x: x[0].lower()):
            variant, status, text = message
            if status == "OK":
                if args.verbose:
                    print('{}: {}'.format(status, text))
            else:
                print('{}: {}'.format(status, text), file=sys.stderr)

if __name__ == '__main__':
  main()

