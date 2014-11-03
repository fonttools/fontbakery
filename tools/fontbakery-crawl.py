#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from __future__ import print_function

import argparse
import copy
import os
import sys
import subprocess
import threading
import traceback

from scrapy import cmdline
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings

from bakery_cli.scrapes import familynames
from bakery_cli.utils import get_data_directory

CRAWLER_TIMEOUT = 60


class cd(object):
    def __init__(self, new_path):
        self.new_path = new_path

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


class RunCrawlerCommand(object):
    def __init__(self, cmd, **kwargs):
        self.env = os.environ.copy()
        self.env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
        self.cmd = cmd
        self.verbose = kwargs.get('verbose', False)
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            close_fds=True, env=self.env)
            if self.verbose:
                stdout = ''
                for line in iter(self.process.stdout.readline, ''):
                    stdout += line
                    self.process.stdout.flush()
                print(stdout)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('\nCommand "{}" has timed out. '
                  '\nTerminating...'.format(self.cmd))
            self.process.terminate()
            self.process.terminate()
            thread.join()

# This script uses 'scrapy' tool by changing directory to the
# FontBakery scrapy project (where scrapy.cfg is located) before execution.

scrapy_args = ['scrapy', ]
parser = argparse.ArgumentParser(description='scrapy wrapper', add_help=False)
parser.add_argument('--verbose', help='Verbose output', action='store_true',
                    default=False)
parser.add_argument('--timeout', type=int,
                    help='Maximum time allocated to crawler', default=60)
args, unknown = parser.parse_known_args()

# if any arguments are given - let `scrapy` to work
if unknown:
    scrapy_args.extend(unknown)
    with cd(os.path.dirname(familynames.__file__)):
        cmdline.execute(scrapy_args)
# otherwise continue with default behavior defined below
else:
    data_dir = get_data_directory()
    crawling_timeout = args.timeout or CRAWLER_TIMEOUT
    crawling_verbose = bool(args.verbose)
    crawling_results = {}

    # allspiders = copy.copy(scrapy_args)
    # allspiders.extend(['allspiders', ])
    # with cd(os.path.dirname(familynames.__file__)):
    #     cmdline.execute(allspiders)

    with cd(os.path.dirname(familynames.__file__)):
        settings = get_project_settings()
        crawler = Crawler(settings)
        spiders_list = crawler.spiders.list()
        for spider in spiders_list:
            print('Crawling with spider: {}'.format(spider))
            spider_args = copy.copy(scrapy_args)
            output_target = os.path.join(data_dir, '{}.json'.format(spider))
            spider_args.extend(
                ['crawl', spider, '-o', output_target, '-t', 'json']
            )
            try:
                command = RunCrawlerCommand(' '.join(spider_args),
                                            verbose=crawling_verbose)
                command.run(timeout=crawling_timeout)
                crawling_results[spider] = 'OK'
            except Exception as exc:
                crawling_results[spider] = 'ERROR'
                print('Spider {} has failed with error: '
                      '{}'.format(spider, traceback.print_exc()))
        print('\nAll crawlers:')
        for k, v in crawling_results.items():
            print('{:<20}{:>5}'.format(k, v))
        print('\nStats are written into "{}" directory'.format(data_dir))
