# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function

import argparse
import collections
import io
import os
import sys


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

    metadataJsonList = []
    for dirpath, dirnames, filenames in os.walk(argv.repo):
        metadataJsonFile = os.path.join(dirpath, 'METADATA.json')
        if not os.path.exists(metadataJsonFile):
            continue
            
        metadataJson = json.load(open(metadataJsonFile))
        try:
            family = metadataJson['name']
        except KeyError:
            print('ER: {} does not contain FamilyName'.format(metadataJsonFile), file=sys.stderr)
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
                fp.write(urllib.urlopen(fonturl).read())
                if argv.verbose:
                    print('OK: {} from {} copied'.format(os.path.basename(cache_font_path), family))

        for subset in webfontsItem['subsets']:
            if subset not in metadataJson['subsets']:
                print('ER: {} has {} in API but not in Github'.format(family, subset), file=sys.stderr)
            elif argv.verbose:
                print('OK: {} has {} in Github and API'.format(family, subset))

        for subset in metadataJson['subsets']:
            if subset not in webfontsItem['subsets']:
                print('ER: {} has {} in Github but not in API'.format(family, subset), file=sys.stderr)

        for style in webfontStyles:
            try:
                filenameWeightStyleIndex = [str(item['weight']) + str(item['style']) for item in metadataJson['fonts']].index(style)
                metadataJsonFileName = metadataJson['fonts'][filenameWeightStyleIndex]['filename']
                if argv.verbose:
                    print('OK: {} in Github and in API'.format(metadataJsonFileName))

                    import hashlib
                    github_md5 = hashlib.md5(open(os.path.join(dirpath, metadataJsonFileName),'rb').read()).hexdigest()
                    fonturl = webfontsItem['files'][style]
                    fontpath = get_cache_font_path(argv.cache, fonturl)
                    google_md5 = hashlib.md5(open(fontpath, 'rb').read()).hexdigest()

                    if github_md5 == google_md5 and argv.verbose:
                        print('OK: {} in production'.format(metadataJsonFileName))

                    if metadataJson['visibility'] == 'External' and argv.verbose:
                        print('OK: {} visibility'.format(family))
                    elif not argv.autofix:
                        print('ER: {} visibility is "{}" should be "External"'.format(family, metadataJson['visibility']), file=sys.stderr)
                    elif argv.autofix:
                        visibility = metadataJson['visibility']
                        
                        from bakery_cli.scripts.genmetadata import striplines
                        content = {}
                        with io.open(metadataJsonFile, 'r', encoding="utf-8") as fp:
                            content = json.load(fp, object_pairs_hook=collections.OrderedDict)

                        content['visibility'] == 'External'
                        with io.open(metadataJsonFile + '.fix', 'w', encoding='utf-8') as f:
                            contents = json.dumps(content, indent=2, ensure_ascii=False)
                            f.write(striplines(contents))

                        print('ER: {} visibility is "{}" is now "External"'.format(family, visibility), file=sys.stderr)
            except ValueError:
                print('ER: {}-{} in API but not in Github'.format(family, style), file=sys.stderr)

        for font in metadataJson['fonts']:
            try:
                webfontStyles.index(str(font['weight']) + str(font['style']))
            except ValueError:
                print('ER: {} in Github but not in API'.format(font['filename']), file=sys.stderr)

        metadataJsonList.append(metadataJsonFile)

