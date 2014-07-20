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

            with patch('bakery.project.models.Project.read_bakery') as read_conf:
                read_conf.return_value = {}

                with patch('bakery.project.models.Project.save_bakery') as save_conf:
                    transaction.execute()
                    save_conf.assert_called_with({'commit': 'master'})
