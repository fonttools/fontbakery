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
import unittest

from mock import patch


class TestTransactionCheckout(unittest.TestCase):

    def test_transaction_raises_exception_if_not_setup(self):
        from bakery.project.views import (CheckoutTransaction,
                                          TransactionException)
        transaction = CheckoutTransaction({})
        with patch.object(CheckoutTransaction, 'project_setup') as ps:
            ps.return_value = False
            self.assertRaises(TransactionException, transaction.execute)

    def test_transaction_changes_commit_in_bakery(self):
        from bakery.project.views import CheckoutTransaction
        from bakery.project.models import Project

        transaction = CheckoutTransaction(Project())
        with patch.object(CheckoutTransaction, 'project_setup') as ps:
            ps.return_value = True

            with patch.object(CheckoutTransaction, 'checkout'):

                with patch('bakery.project.models.Project.read_bakery') as read_conf:
                    read_conf.return_value = {}

                    with patch('bakery.project.models.Project.save_bakery') as save_conf:

                        transaction.execute()

                    save_conf.assert_called_with({'commit': 'master'})
