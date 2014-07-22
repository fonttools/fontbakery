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
from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckMagicPREPByteCode(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'
    longMessage = True

    def test_prep_magic_code(self):
        """ Font contains in PREP table magic code """
        magiccode = '\xb8\x01\xff\x85\xb0\x04\x8d'
        font = Font.get_ttfont(self.path)
        try:
            bytecode = font.get_program_bytecode()
        except KeyError:
            bytecode = ''
        self.assertTrue(bytecode == magiccode,
                        msg='PREP does not contain magic code')
