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
import re


class RedisFd(object):
    """ Redis File Descriptor class, publish writen data to redis channel
        in parallel to file """
    def __init__(self, name, mode='a', write_pipeline=None):
        self.filed = open(name, mode)
        self.filed.write("Start: Start of log\n")  # end of log
        self.write_pipeline = write_pipeline
        if write_pipeline and not isinstance(write_pipeline, list):
            self.write_pipeline = [write_pipeline]

    def write(self, data, prefix=''):
        if self.write_pipeline:

            for pipeline in self.write_pipeline:
                data = pipeline(data)

        if not data.endswith('\n'):
            data += '\n'

        data = re.sub('\n{3,}', '\n\n', data)
        if data:
            self.filed.write("%s%s" % (prefix, data))
            self.filed.flush()

    def close(self):
        self.filed.write("End: End of log\n")  # end of log
        self.filed.close()
