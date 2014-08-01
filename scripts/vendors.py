from __future__ import print_function
import argparse
import csv
import json
import os
import sys
import re


regex = re.compile(("((?:[\w]+)[\w.-]+@[\w.-]+\w{2,4})"), re.U | re.S)


class CSVVendorWriter(object):

    def __init__(self):
        self.writer = csv.writer(sys.stdout, delimiter=',',
                                 quoting=csv.QUOTE_MINIMAL)

    def writerow(self, data):
        row = []

        if not isinstance(data, list):
            data = [data]

        for r in data:
            if isinstance(r, list):
                row.append(','.join(map(lambda x: x.encode('utf8', 'xmlcharrefreplace'), r)))
            else:
                row.append(r.encode('utf8', 'xmlcharrefreplace'))
        self.writer.writerow(row)


def extract_emails_from_string(string):
    string = string.lower()
    return regex.findall(string)


def extract_urls_from_string(string):
    regex = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    return [x[0] for x in regex.findall(string)]


def extract_designers_from_string(string):
    return []


def main(options):
    print('Looping ', os.path.abspath(options.directory))
    writer = CSVVendorWriter()
    for root, dirs, files in os.walk(options.directory):
        metadata_file = os.path.join(root, 'METADATA.json')
        if os.path.exists(metadata_file):
            metadata = json.load(open(metadata_file))

            designers = [metadata.get('designer', '')]
            urls = []
            emails = []

            for font in metadata.get('fonts', []):
                emails += extract_emails_from_string(font.get('copyright', ''))
                urls += extract_urls_from_string(font.get('copyright', ''))

            writer.writerow([metadata['name'],
                             list(set(designers)),
                             list(set(emails)),
                             list(set(urls))])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')

    options = parser.parse_args()

    main(options)
