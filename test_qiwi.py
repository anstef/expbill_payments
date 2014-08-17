# -*- coding: utf-8 -*-

import unittest
import mock
import json
import sqlite3
import re

from qiwi import Qiwi, PaymentTransaction, QiwiProcessException, settings, requests, error_logger, success_logger


class QiwiTest(unittest.TestCase):
    def setUp(self):
        error_logger.disabled = True
        success_logger.disabled = True
        settings.db_name = '/tmp/test_payments1.db'
        self.qiwi = Qiwi()

    def tearDown(self):
        if self.qiwi.conn:
            self.qiwi.conn.commit()
            self.qiwi.conn.close()

        conn = sqlite3.connect(settings.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM transactions")
        conn.commit()
        conn.close()


@mock.patch.object(requests.Session, 'post')
@mock.patch.object(requests.Session, 'get')
class TestLastPaymentsPage(QiwiTest):
    def test_success(self, mock_get, mock_post):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = json.dumps({'data': {'token': 123456789}})
        mock_post.return_value = post_resp_mock

        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        mock_get.return_value = get_resp_mock

        self.qiwi.get_last_payments_page()

        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(
            str(mock_post.call_args_list[0]),
            "call('%s', headers={'X-Requested-With': 'XMLHttpRequest', "
            "'Accept': 'application/json, text/javascript, */*; q=0.01'}, "
            "data={'source': 'MENU', 'login': '%s', 'password': '%s'})" %
            (settings.qiwi_login_url, settings.qiwi_login, settings.qiwi_pass))
        self.assertEqual(
            str(mock_post.call_args_list[1]),
            "call('%s', headers={'X-Requested-With': 'XMLHttpRequest', "
            "'Accept': 'application/json, text/javascript, */*; q=0.01'}, "
            "data={'source': 'MENU', 'login': '%s', 'password': '%s', 'loginToken': 123456789})" %
            (settings.qiwi_login_url, settings.qiwi_login, settings.qiwi_pass))
        self.assertEqual(
            str(mock_get.call_args_list[0]),
            "call('%s')" % (settings.qiwi_payments_url))

    def test_failed_auth(self, mock_get, mock_post):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 404
        mock_post.return_value = post_resp_mock

        with self.assertRaises(QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_token(self, mock_get, mock_post):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = json.dumps({'data': {'smth': 123456789}})
        mock_post.return_value = post_resp_mock

        with self.assertRaises(QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_data(self, mock_get, mock_post):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = json.dumps({'test': 123})
        mock_post.return_value = post_resp_mock

        with self.assertRaises(QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_resp_json(self, mock_get, mock_post):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = 'test'
        mock_post.return_value = post_resp_mock

        with self.assertRaises(QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_invalid_get(self, mock_get, mock_post):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 400
        mock_get.return_value = get_resp_mock

        with self.assertRaises(QiwiProcessException):
            self.qiwi.get_last_payments_page()


class PaymentsParsingTest(QiwiTest):
    def test_success(self):
        import test_qiwi_data
        payments = self.qiwi.parse_payments_page(re.sub('\n', '', test_qiwi_data.valid_body))
        self.assertEqual(len(payments), 2)
        self.assertEqual(payments[0].trans_id, '999999900352844497')
        self.assertEqual(payments[0].sum, '2.00')
        self.assertEqual(payments[0].payer, 'nc _123-456')
        self.assertEqual(payments[0].comment, u'Visa QIWI Walletsome info')
        self.assertEqual(payments[1].trans_id, '999999900352843708')
        self.assertEqual(payments[1].sum, '1001.50')
        self.assertEqual(payments[1].payer, '234-567')
        self.assertEqual(payments[1].comment, u'Visa QIWI Walletsome info')

    def test_fail(self):
        payments = self.qiwi.parse_payments_page('')
        self.assertEqual(payments, [])


class PaymentTransactionTest(QiwiTest):
    def test_process(self):
        payment = PaymentTransaction(self.qiwi.cur, u'123456', u'100.66 руб.', u'123-456', u'test comment')
        self.assertFalse(payment.is_processed())
        payment.process()
        self.assertTrue(payment.is_processed())

    @mock.patch.object(requests, 'get')
    def test_success_billing_payment(self, get_mock):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        get_resp_mock.text = '1'
        get_mock.return_value = get_resp_mock

        payment = PaymentTransaction(self.qiwi.cur, u'123456', u'100.66 руб.', u'#t12_34-56', u'test comment')
        payment.save()
        get_mock.assert_called_once_with(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'#t12_34-56',
                    'secret': '12345678901234567890hgh55g54'})

    @mock.patch.object(requests, 'get')
    def test_fix_account_misprint(self, get_mock):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 200
        get_resp_mock.text = '-1'
        get_mock.return_value = get_resp_mock

        payment = PaymentTransaction(self.qiwi.cur, u'123456', u'100.66 руб.', u'#t12_34-56', u'test comment')
        payment.save()
        self.assertEqual(get_mock.call_count, 3)
        self.assertEqual(get_mock.call_args_list[0], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u'#t12_34-56',
                    'secret': '12345678901234567890hgh55g54'}))
        self.assertEqual(get_mock.call_args_list[1], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u't12_34-56',
                    'secret': '12345678901234567890hgh55g54'}))
        self.assertEqual(get_mock.call_args_list[2], mock.call(
            settings.billing_payment_url,
            params={'sum': u'100.66',
                    'trans': u'123456',
                    'uid': u't12_3456',
                    'secret': '12345678901234567890hgh55g54'}))

