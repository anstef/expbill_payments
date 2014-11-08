# -*- coding: utf-8 -*-

import unittest
import mock
import sqlite3

import settings
from transactions import base_transaction


@mock.patch.object(base_transaction, 'send_email')
@mock.patch.object(base_transaction.requests, 'get')
class PaymentTransactionTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect('/tmp/test_payments1.db')
        self.cur = self.conn.cursor()
        base_transaction.error_logger.disabled = True
        base_transaction.success_logger.disabled = True

    def tearDown(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM transactions")
        self.conn.commit()
        self.conn.close()

    def test_process(self, get_mock, send_email_mock):
        payment = base_transaction.BaseTransaction(self.cur, u'123456', u'100.66 руб.', u'123-456', u'test comment')
        self.assertFalse(payment.is_processed())
        payment.process()
        self.assertTrue(payment.is_processed())

    def test_success_billing_payment(self, get_mock, send_email_mock):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        get_resp_mock.text = '1'
        get_mock.return_value = get_resp_mock

        payment = base_transaction.BaseTransaction(self.cur, u'123456', u'100.66 руб.', u'#t12_34-56', u'test comment')
        payment.save()
        get_mock.assert_called_once_with(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'#t12_34-56',
                    'secret': settings.billing_secret})

    def test_fix_account_misprint(self, get_mock, send_email_mock):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        get_resp_mock.text = '-1'
        get_mock.return_value = get_resp_mock

        payment = base_transaction.BaseTransaction(self.cur, u'123456', u'100.66 руб.', u'#t12_34-56', u'test comment')
        payment.save()
        self.assertEqual(get_mock.call_count, 3)
        self.assertEqual(get_mock.call_args_list[0], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'#t12_34-56',
                    'secret': settings.billing_secret}))
        self.assertEqual(get_mock.call_args_list[1], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u't12_34-56',
                    'secret': settings.billing_secret}))
        self.assertEqual(get_mock.call_args_list[2], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'1234-56',
                    'secret': settings.billing_secret}))
        self.assertTrue(send_email_mock.called)

    def test_replace_cyrilic(self, get_mock, send_email_mock):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        get_resp_mock.text = '-1'
        get_mock.return_value = get_resp_mock

        payment = base_transaction.BaseTransaction(
            self.cur, u'123456', u'100.66 руб.', u'а123абвдеклмнорстхю', u'test comment')
        payment.save()

        self.assertEqual(get_mock.call_args_list[0], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'a123abbdeklmnopctxu',
                    'secret': settings.billing_secret}))