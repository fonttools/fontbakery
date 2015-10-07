# -*- coding: utf-8 -*-
#!/usr/bin/env python
from __future__ import print_function

import argparse
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
		except ValueError:
			print('ER: {} is not in production'.format(family))
			continue

		for style, fonturl in webfontList[index]['files'].items():
			urlparts = urlparse.urlparse(fonturl)
			cache_dir = argv.cache
			cache_dir = os.path.join(cache_dir, urlparts.netloc, os.path.dirname(urlparts.path).strip('/'))
			if not os.path.exists(cache_dir):
				os.makedirs(cache_dir)

			fontname = os.path.basename(fonturl)

			if argv.ignore_copy_existing_ttf and os.path.exists(os.path.join(cache_dir, fontname)):
				continue

			with open(os.path.join(cache_dir, fontname), 'w') as fp:
				fp.write(urllib.urlopen(fonturl).read())
				if argv.verbose:
					print('OK: {} from {} copied'.format(fontname, family))

		for subset in webfontList[index]['subsets']:
			if subset not in metadataJson['subsets']:
				print('ER: {} has {} in API but not in Github'.format(family, subset), file=sys.stderr)
			elif argv.verbose:
				print('OK: {} has {} in Github and API'.format(family, subset))

		for subset in metadataJson['subsets']:
			if subset not in webfontList[index]['subsets']:
				print('ER: {} has {} in Github but not in API'.format(family, subset), file=sys.stderr)		

		metadataJsonList.append(metadataJsonFile)

