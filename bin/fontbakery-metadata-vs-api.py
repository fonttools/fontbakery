#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys
import urllib
import urlparse
import json
from fonts_public_pb2 import FamilyProto
from google.protobuf import text_format

parser = argparse.ArgumentParser()
parser.add_argument('key', help='Key from Google Fonts Developer API')
parser.add_argument('repo', help='Directory tree that contains directories with METADATA.pb files')
parser.add_argument('--cache', help='Directory to store a copy of the files in the fonts developer api',
                    default="/tmp/fontbakery-compare-git-api")
parser.add_argument('--verbose', help='Print additional information', action="store_true")
parser.add_argument('--ignore-copy-existing-ttf', action="store_true")
parser.add_argument('--autofix', help='Apply automatic fixes to files', action="store_true")
parser.add_argument('--api', help='Domain string to use to request', default="fonts.googleapis.com")


def get_cache_font_path(cache_dir, fonturl):
    urlparts = urlparse.urlparse(fonturl)
    cache_dir = os.path.join(cache_dir, urlparts.netloc, os.path.dirname(urlparts.path).strip('/'))
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


def main():
    args = parser.parse_args()
    response = urllib.urlopen('https://www.googleapis.com/webfonts/v1/webfonts?key={}'.format(args.key))
    try:
        webfontList = json.loads(response.read())['items']
        webfontListFamilyNames = [item['family'] for item in webfontList]
    except (ValueError, KeyError):
        sys.exit(1)

    for dirpath, dirnames, filenames in os.walk(args.repo):
        metadataProtoFile = os.path.join(dirpath, 'METADATA.pb')
        if not os.path.exists(metadataProtoFile):
            continue

        metadata = FamilyProto()
        text_data = open(metadataProtoFile, "rb").read()
        text_format.Merge(text_data, metadata)
        try:
            family = metadata.name
        except KeyError:
            print('ER: "{}" does not contain FamilyName'.format(metadataProtoFile), file=sys.stderr)
            continue

        try:
            index = webfontListFamilyNames.index(family)
            webfontsItem = webfontList[index]
        except ValueError:
            print('ER: Family "{}" could not be found in API'.format(family))
            continue

        webfontVariants = []
        log_messages = []
        for variant, fonturl in webfontsItem['files'].items():
            cache_font_path = get_cache_font_path(args.cache, fonturl)
            webfontVariants.append(variant)

            if args.ignore_copy_existing_ttf and os.path.exists(cache_font_path):
                continue

            with open(cache_font_path, 'w') as fp:
                filenameWeightStyleIndex = [getVariantName(item) for item in metadata.fonts].index(variant)
                filename = metadata.fonts[filenameWeightStyleIndex].filename
                if args.verbose:
                    print('Downloading "{}" as "{}"'.format(fonturl, filename))

                #Saving:
                fp.write(urllib.urlopen(fonturl).read())

                #Symlinking:
                src = cache_font_path
                dst_dir = os.path.dirname(cache_font_path)
                dst = os.path.join(dst_dir, filename)
                if not os.path.exists(dst):
                    os.symlink(src, dst)

        for subset in webfontsItem['subsets']:
            if subset == "menu":
                # note about Google Web Fonts:
                # Menu subsets are no longer generated offline.
                continue

            if subset not in metadata.subsets:
                print('ER: "{}" lacks subset "{}" in git'.format(family, subset), file=sys.stderr)
            else:
                if args.verbose:
                    print('OK: "{}" subset "{}" in sync'.format(family, subset))

        for subset in metadata.subsets:
            if subset != "menu" and subset not in webfontsItem['subsets']:
                print('ER: "{}" lacks subset "{}" in API'.format(family, subset), file=sys.stderr)

        if metadata.category.lower() != webfontsItem['category']:
            print('ER: "{}" category "{}" in git does not match category "{}" in API'.format(family, metadata.category, webfontsItem['category']))
        else:
            if args.verbose:
                print('OK: "{}" category "{}" in sync'.format(family, metadata.category))


        for variant in webfontVariants:
            try:
                filenameWeightStyleIndex = [getVariantName(item) for item in metadata.fonts].index(variant)
                repoFileName = metadata.fonts[filenameWeightStyleIndex].filename

                fonturl = webfontsItem['files'][variant]
                fontpath = get_cache_font_path(args.cache, fonturl)

                import hashlib
                google_md5 = hashlib.md5(open(fontpath, 'rb').read()).hexdigest()
                repo_md5 = hashlib.md5(open(os.path.join(dirpath, repoFileName), 'rb').read()).hexdigest()

                if repo_md5 == google_md5:
                    log_messages.append([variant, 'OK', '"{}" in sync'.format(repoFileName)])
                else:
                    log_messages.append([variant, 'ER', '"{}" checksum mismatch, file in API does not match file in git'.format(repoFileName)])

            except ValueError:
                log_messages.append([variant, 'ER', '"{}" available in API but not in git'.format(font.filename)])

        for font in metadata.fonts:
            variant = getVariantName(font)
            try:
                webfontVariants.index(variant)
            except ValueError:
                log_messages.append([variant, 'ER', '"{}" available in git but not in API'.format(font.filename)])

        #sort all the messages by their respective metadataFileName and print them:
        for message in sorted(log_messages, key=lambda x: x[0].lower()):
            variant, status, text = message
            if status == "OK":
                if args.verbose:
                    print('{}: {}'.format(status, text))
            else:
                print('{}: {}'.format(status, text), file=sys.stderr)

if __name__ == '__main__':
  main()

