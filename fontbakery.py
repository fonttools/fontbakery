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
import sys
import yaml


from cli.bakery import Bakery, BAKERY_CONFIGURATION_DEFAULTS


class systdout:

    @staticmethod
    def write(msg, prefix=''):
        sys.stdout.write(prefix + msg)


def main(path):
    rootpath = os.path.dirname(path)

    config = yaml.safe_load(open(BAKERY_CONFIGURATION_DEFAULTS))

    if path[-4:] in ['.ufo', '.ttx', '.ttf', '.otf', '.sfd']:
        # create config bakery.yaml from defaults
        if 'process_files' not in config:
            config['process_files'] = []
        config['process_files'].append(os.path.basename(path))

    l = open(os.path.join(rootpath, '.bakery.yaml'), 'w')
    l.write(yaml.safe_dump(config))
    l.close()

    b = Bakery(os.path.join(rootpath, '.bakery.yaml'), stdout_pipe=systdout)
    b.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help=("Path to source project. It can also be "
                              "UFO, TTX, TTF or OTF files"))
    args = parser.parse_args()
    main(args.filename)
