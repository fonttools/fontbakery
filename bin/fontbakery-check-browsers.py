#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
fontbakery-browser-tests
~~~~~~~~~~~~~~~~~~~~~~~~

Use BrowserStack and GF Regression to take a waterfall screenshot of
a collection of fonts on a range of Browsers.

TODO (Marc Foley) Once Diffenator matures, return differences... not 
just a waterfall.
"""
import argparse
import sys
from PIL import Image
import browserstack_screenshots
import requests
import os
from glob import glob
from ntpath import basename
import time
import json

from fontbakery.browserdata import config_browsers

CONFIG = 'browser_config.json'


def _build_filename_from_browserstack_json(j):
    """Build useful filename for an image from the screenshot json metadata"""
    filename = ''
    device = j['device'] if j['device'] else 'Desktop'
    if j['state'] == 'done' and j['image_url']:
        detail = [device, j['os'], j['os_version'],
                  j['browser'], j['browser_version'], '.jpg']
        filename = '_'.join(item.replace(" ", "_") for item in detail if item)
    else:
        print 'screenshot timed out, ignoring this result'
    return filename


def _download_file(uri, filename):
    try:
        with open(filename, 'wb') as handle:
            request = requests.get(uri, stream=True)
            for block in request.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    except IOError, e:
        print e


def _mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def gen_browserstack_imgs(auth, website, out_dir):
    _mkdir(out_dir)

    config = config_browsers
    config['url'] = website

    bstack = browserstack_screenshots.Screenshots(auth=auth, config=config)
    generate_resp_json = bstack.generate_screenshots()
    job_id = generate_resp_json['job_id']
    print "http://www.browserstack.com/screenshots/{0}".format(job_id)
    screenshots_json = bstack.get_screenshots(job_id)
    print 'Generating images, be patient'
    while screenshots_json == False: # keep refreshing until browerstack is done
        time.sleep(3)
        screenshots_json = bstack.get_screenshots(job_id)
    for screenshot in screenshots_json['screenshots']:
        filename = _build_filename_from_browserstack_json(screenshot)
        base_image = os.path.join(out_dir, filename)
        if filename:
            _download_file(screenshot['image_url'], base_image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('username', help='Browserstack username')
    parser.add_argument('auth_key', help='Browserstack auth key')
    parser.add_argument('fonts', nargs="+", help="Font paths")
    parser.add_argument('-d', '--output-dir',
                        help="Directory to output images to")
    args = parser.parse_args()
    auth = (args.username, args.auth_key)
    out_dir = args.output_dir if args.output_dir else os.getcwd()

    # Send fonts to GF Regression
    url_gfregression = 'http://45.55.138.144'
    url_upload = url_gfregression + '/api/upload'
    payload = [('fonts', open(f, 'rb')) for f in args.fonts]
    request = requests.post(url_upload, files=payload)
    url_screenshot = url_gfregression + request.content

    gen_browserstack_imgs(auth, url_screenshot, out_dir)


if __name__ == '__main__':
    main()