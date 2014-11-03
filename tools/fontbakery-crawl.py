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

import argparse
import os

from scrapy import cmdline

from bakery_cli.scrapes import familynames


class cd(object):
    def __init__(self, new_path):
        self.new_path = new_path

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

# This script just calls 'scrapy' tool by changing directory to the
# FontBakery scrapy project (where scrapy.cfg is located) before execution.

scrapy_args = ['scrapy', ]
parser = argparse.ArgumentParser(description='scrapy wrapper', add_help=False)
args, unknown = parser.parse_known_args()
scrapy_args.extend(unknown)

with cd(os.path.dirname(familynames.__file__)):
    cmdline.execute(scrapy_args)
