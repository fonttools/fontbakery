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
import shutil
import sys
import yaml


from cli.bakery import Bakery, BAKERY_CONFIGURATION_DEFAULTS


class systdout:

    @staticmethod
    def write(msg, prefix=''):
        sys.stdout.write(prefix + msg)


def main(sources, config):

    rootpath = os.path.abspath('build/tmp')
    if not config:
        config = yaml.safe_load(open(BAKERY_CONFIGURATION_DEFAULTS))
    else:
        config = yaml.safe_load(open(config))

    if 'process_files' not in config:
        config['process_files'] = []

    for source in sources:
        if source[-4:] in ['.ufo', '.ttx', '.ttf', '.otf', '.sfd']:
            # create config bakery.yaml from defaults
            config['process_files'].append(source)
        else:
            continue
        if os.path.isdir(source):
            shutil.copytree(source, rootpath)
        else:
            shutil.copy(source, rootpath)

    l = open(os.path.join(rootpath, '.bakery.yaml'), 'w')
    l.write(yaml.safe_dump(config))
    l.close()

    try:
        b = Bakery(os.path.join(rootpath, '.bakery.yaml'),
                   stdout_pipe=systdout)
        b.interactive = True
        b.run(with_upstream=True)
    finally:
        shutil.rmtree(rootpath)
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs="+",
                        help=("Path to UFO, SFD, TTX, TTF or OTF files"))
    parser.add_argument('--config', type=str, default='')
    args = parser.parse_args()
    main(args.filename, args.config)
