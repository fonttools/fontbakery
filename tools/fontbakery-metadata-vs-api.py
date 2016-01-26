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
args.add_argument('repo', help='Directory tree that contains directories with METADATA.pb files')
args.add_argument('--cache', help='Directory to store a copy of the files in the fonts developer api',
                  default="/tmp/fontbakery-compare-git-api")
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
            print('ER: Family "{}" could not be found in API'.format(family))
            continue

        webfontVariants = []
        log_messages = []
        for variant, fonturl in webfontsItem['files'].items():
            cache_font_path = get_cache_font_path(argv.cache, fonturl)
            webfontVariants.append(variant)

            if argv.ignore_copy_existing_ttf and os.path.exists(cache_font_path):
                continue

            with open(cache_font_path, 'w') as fp:
                if argv.verbose:
                    print("Downloading '{} {}' from {}".format(family, variant, fonturl))

                #Saving:
                fp.write(urllib.urlopen(fonturl).read())

                #Symlinking:
                src = cache_font_path
                dst_dir = os.path.dirname(cache_font_path)
                dst = os.path.join(dst_dir, '{}-{}.ttf'.format(family, variant))
                if not os.path.exists(dst):
                    os.symlink(src, dst)

                #Reporting:
                log_messages.append([variant, 'OK', 'Saved to {}'.format(dst)])

        for subset in webfontsItem['subsets']:
            if subset == "menu":
                # note about Google Web Fonts:
                # Menu subsets are no longer generated offline.
                continue

            if subset not in metadata.subsets:
                print('ER: {} has subset "{}" in API but not in repository'.format(family, subset), file=sys.stderr)
            else:
                if argv.verbose:
                    print('OK: {} has subset {} in repository and API'.format(family, subset))

        for subset in metadata.subsets:
            if subset != "menu" and subset not in webfontsItem['subsets']:
                print('ER: {} has subset {} in repository but not in API'.format(family, subset), file=sys.stderr)

        def getVariantName(item):
            if item.style == "normal" and item.weight == 400:
                return "regular"

            name = ""
            if item.weight != 400:
                name = str(item.weight)

            if item.style != "normal":
                name += item.style

            return name

        for variant in webfontVariants:
            try:
                filenameWeightStyleIndex = [getVariantName(item) for item in metadata.fonts].index(variant)
                repoFileName = metadata.fonts[filenameWeightStyleIndex].filename

                fonturl = webfontsItem['files'][variant]
                fontpath = get_cache_font_path(argv.cache, fonturl)

                import hashlib
                google_md5 = hashlib.md5(open(fontpath, 'rb').read()).hexdigest()
                repo_md5 = hashlib.md5(open(os.path.join(dirpath, repoFileName), 'rb').read()).hexdigest()

                if repo_md5 == google_md5:
                    log_messages.append([variant, 'OK', '{} is identical in repository and API'.format(repoFileName)])
                else:
                    log_messages.append([variant, 'ER', '{}: Checksum mismatch: File in API does not match file in repository'.format(repoFileName)])

            except ValueError:
                log_messages.append([variant, 'ER', 'Available in API but not in repository'])

        for font in metadata.fonts:
            variant = getVariantName(font)
            try:
                webfontVariants.index(variant)
            except ValueError:
                log_messages.append([variant, 'ER', 'Available in repository but not in API'.format(font.filename)])

        #sort all the messages by their respective metadataFileName and print them:
        for message in sorted(log_messages, key=lambda x: x[0].lower()):
            variant, status, text = message
            if status == "OK":
                if argv.verbose:
                    print("{}: [{} {}] {}".format(status, family, variant, text))
            else:
                print("{}: [{} {}] {}".format(status, family, variant, text), file=sys.stderr)

