# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function

import argparse
import collections
import io
import os
import sys
import fonts_public_pb2 as fonts_pb2
from google.protobuf import text_format

args = argparse.ArgumentParser()
args.add_argument('key', help='Key from Google Fonts Developer API')
args.add_argument('repo', help='Directory tree that contains directories with METADATA.json')
args.add_argument('--cache', help='Directory to store a copy of the files in the fonts developer api',
                  default="/tmp/fontbakery-compare-github-api")
args.add_argument('--verbose', help='Print additional information', action="store_true")
args.add_argument('--ignore-copy-existing-ttf', action="store_true")
args.add_argument('--autofix', help='Apply automatic fixes to files', action="store_true")
args.add_argument('--api', help='Domain string to use to request', default="fonts.googleapis.com")
argv = args.parse_args()


def get_cache_font_path(cache_dir, fonturl):
    urlparts = urlparse.urlparse(fonturl)
    cache_dir = os.path.join(cache_dir, urlparts.netloc, os.path.dirname(urlparts.path).strip('/'))
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fontname = os.path.basename(fonturl)
    return os.path.join(cache_dir, fontname)


if __name__ == '__main__':
    import urllib
    import urlparse
    import json
    response = urllib.urlopen('https://www.googleapis.com/webfonts/v1/webfonts?key={}'.format(argv.key))
    try:
        webfontList = json.loads(response.read())['items']
        webfontListFamilyNames = [item['family'] for item in webfontList]
    except (ValueError, KeyError):
        sys.exit(1)

    for dirpath, dirnames, filenames in os.walk(argv.repo):
        metadataProtoFile = os.path.join(dirpath, 'METADATA.pb')
        if not os.path.exists(metadataProtoFile):
            continue

        metadata = fonts_pb2.FamilyProto()
        text_data = open(metadataProtoFile, "rb").read()
        text_format.Merge(text_data, metadata)
        try:
            family = metadata.name
        except KeyError:
            print('ER: {} does not contain FamilyName'.format(metadataProtoFile), file=sys.stderr)
            continue

        try:
            index = webfontListFamilyNames.index(family)
            webfontsItem = webfontList[index]
        except ValueError:
            print('ER: {} is not in production'.format(family))
            continue

        webfontStyles = []
        for style, fonturl in webfontsItem['files'].items():
            cache_font_path = get_cache_font_path(argv.cache, fonturl)
            webfontStyles.append(style)

            if argv.ignore_copy_existing_ttf and os.path.exists(cache_font_path):
                continue

            with open(cache_font_path, 'w') as fp:
                if argv.verbose:
                    print("Downloading '{} {}' from {}".format(family, style, fonturl))
                fp.write(urllib.urlopen(fonturl).read())
                if argv.verbose:
                    print('OK: [{} {}] Saved to {}'.format(family, style, cache_font_path))

        for subset in webfontsItem['subsets']:
            if subset == "menu":
                # note about Google Web Fonts:
                # Menu subsets are no longer generated offline.
                continue

            if subset not in metadata.subsets:
                print('ER: {} has {} in API but not in Github'.format(family, subset), file=sys.stderr)
            elif argv.verbose:
                print('OK: {} has {} in Github and API'.format(family, subset))

        for subset in metadata.subsets:
            if subset != "menu" and subset not in webfontsItem['subsets']:
                print('ER: {} has {} in Github but not in API'.format(family, subset), file=sys.stderr)

        log_messages = []
        for style in webfontStyles:
            try:
                filenameWeightStyleIndex = [str(item.weight) + str(item.style) for item in metadata.fonts].index(style)
                metadataFileName = metadata.fonts[filenameWeightStyleIndex].filename
                if argv.verbose:
                    log_messages.append([metadataFileName, 'OK', '{} in Github and in API'.format(metadataFileName)])

                    import hashlib
                    github_md5 = hashlib.md5(open(os.path.join(dirpath, metadataFileName), 'rb').read()).hexdigest()
                    fonturl = webfontsItem['files'][style]
                    fontpath = get_cache_font_path(argv.cache, fonturl)
                    google_md5 = hashlib.md5(open(fontpath, 'rb').read()).hexdigest()

                    if github_md5 == google_md5:
                        if argv.verbose:
                            log_messages.append([metadataFileName, 'OK', '{} in production'.format(metadataFileName)])
                    else:
                        log_messages.append([metadataFileName, 'ER', '{}: File in API does not match file in production (checksum mismatch)'.format(metadataFileName)])
            except ValueError:
                name = '{}-{}'.format(family, style)
                log_messages.append([name, 'ER', '{} in API but not in Github'.format(name)])

        for font in metadata.fonts:
            try:
                webfontStyles.index(str(font.weight) + str(font.style))
            except ValueError:
                log_messages.append([font.filename, 'ER', '{} in Github but not in API'.format(font.filename)])

        #sort all the messages by their respective metadataFileName and print them:
        for message in sorted(log_messages, key=lambda x: x[0].lower()):
            _, status, text = message
            if status == "OK":
                print("{}: {}".format(status, text))
            else:
                print("{}: {}".format(status, text), file=sys.stderr)

