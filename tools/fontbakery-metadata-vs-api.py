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
args.add_argument('--autofix', help='Apply automatic fixes to files', action="store_true")
args.add_argument('--api', help='Domain string to use to request', default="fonts.googleapis.com")
argv = args.parse_args()


if __name__ == '__main__':
	import urllib
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
		if os.path.exists(metadataJsonFile):
			
			metadataJson = json.load(open(metadataJsonFile))
			try:
				family = metadataJson['name']
				if family not in webfontListFamilyNames:
					print('ER: {} is not in production'.format(family))
					continue
			except KeyError:
				print('ER: {} does not contain FamilyName'.format(metadataJsonFile), file=sys.stderr)
				continue
			
			metadataJsonList.append(metadataJsonFile)