# -*- coding: utf-8 -*-

import re
import mock
import unittest
import json
import sqlite3

from providers import qiwi
from tests import qiwi_data
from transactions import base_transaction


class QiwiTest(unittest.TestCase):
    def setUp(self):
        qiwi.error_logger.disabled = True
        qiwi.success_logger.disabled = True
        qiwi.settings.db_name = '/tmp/test_payments1.db'
        self.qiwi = qiwi.Qiwi()

    def tearDown(self):
        if self.qiwi.conn:
            self.qiwi.conn.close()

        conn = sqlite3.connect(qiwi.settings.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM transactions")
        conn.commit()
        conn.close()


@mock.patch.object(base_transaction, 'send_email')
@mock.patch.object(qiwi.requests.Session, 'post')
@mock.patch.object(qiwi.requests.Session, 'get')
class TestQiwiLastPaymentsPage(QiwiTest):
    def test_success(self, mock_get, mock_post, *args):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 201
        post_resp_mock.text = json.dumps({
            "entity": {
                "user": "+123",
                "ticket": "TGT-123"
            },
            "links": [{"rel": "sts", "href": "https://auth.qiwi.com/cas/sts"}]})
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
            "data={'login': '%s', 'password': '%s'})" %
            (qiwi.settings.qiwi_login_url, qiwi.settings.qiwi_login, qiwi.settings.qiwi_pass))
        self.assertEqual(
            str(mock_post.call_args_list[1]),
            "call(u'https://auth.qiwi.com/cas/sts', headers={'X-Requested-With': 'XMLHttpRequest', "
            "'Accept': 'application/json, text/javascript, */*; q=0.01'}, "
            "data={'ticket': u'TGT-123', 'service': 'https://visa.qiwi.com/j_spring_cas_security_check'})")
        self.assertEqual(
            str(mock_get.call_args_list[0]),
            "call('%s')" % (qiwi.settings.qiwi_payments_url))

    def test_failed_auth(self, mock_get, mock_post, *args):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 404
        mock_post.return_value = post_resp_mock

        with self.assertRaises(qiwi.QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_token(self, mock_get, mock_post, *args):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = json.dumps({'data': {'smth': 123456789}})
        mock_post.return_value = post_resp_mock

        with self.assertRaises(qiwi.QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_data(self, mock_get, mock_post, *args):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = json.dumps({'test': 123})
        mock_post.return_value = post_resp_mock

        with self.assertRaises(qiwi.QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_no_resp_json(self, mock_get, mock_post, *args):
        post_resp_mock = mock.Mock()
        post_resp_mock.status_code = 200
        post_resp_mock.text = 'test'
        mock_post.return_value = post_resp_mock

        with self.assertRaises(qiwi.QiwiProcessException):
            self.qiwi.get_last_payments_page()

    def test_invalid_get(self, mock_get, mock_post, *args):
        get_resp_mock = mock.Mock()
        get_resp_mock.status_code = 400
        mock_get.return_value = get_resp_mock

        with self.assertRaises(qiwi.QiwiProcessException):
            self.qiwi.get_last_payments_page()


@mock.patch.object(base_transaction, 'send_email')
class QiwiPaymentsParsingTest(QiwiTest):
    def test_success(self, *args):
        # emulate processed iransaction
        self.qiwi.cur.execute("INSERT INTO transactions VALUES(123456)")

        payments = self.qiwi.parse_payments_page(re.sub('\n', '', qiwi_data.valid_body))
        self.assertEqual(len(payments), 2)
        self.assertEqual(payments[0].trans_id, '999999900352844497')
        self.assertEqual(payments[0].sum, '2.00')
        self.assertEqual(payments[0].payer, 'nc _123-456')
        self.assertEqual(payments[0].comment, u'Visa QIWI Walletsome info')
        self.assertEqual(payments[1].trans_id, '999999900352843708')
        self.assertEqual(payments[1].sum, '1001.50')
        self.assertEqual(payments[1].payer, '234-567')
        self.assertEqual(payments[1].comment, u'Visa QIWI Walletsome info')

    def test_fail(self, *args):
        payments = self.qiwi.parse_payments_page('')
        self.assertEqual(payments, [])


class TestQiwiProccess(QiwiTest):
    @mock.patch.object(qiwi.Qiwi, 'get_payments')
    @mock.patch.object(base_transaction.BaseTransaction, 'process')
    def test_simple(self, payment_process_mock, get_payments_mock):
        get_payments_mock.return_value = [
            base_transaction.BaseTransaction(self.qiwi.cur, 1, '10', 'payer1', 'test1'),
            base_transaction.BaseTransaction(self.qiwi.cur, 3, '10', 'payer4', 'test4'),
        ]
        self.qiwi.process()
        self.assertEqual(payment_process_mock.call_count, 2)


