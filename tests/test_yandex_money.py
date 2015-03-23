# -*- coding: utf-8 -*-

import mock
import unittest

from providers import yandex_money
from tests import yandex_money_data
from transactions import base_transaction


class YandexMoneyPaymentsParsingTest(unittest.TestCase):
    def setUp(self):
        self.provider = yandex_money.YandexMoney()

    def test_parse_valid_body(self):
        transaction = self.provider.parse_payment_message(yandex_money_data.valid_body)
        self.assertEqual(transaction.payer, 'test_payer')
        self.assertEqual(transaction.sum, u'686')

        transaction = self.provider.parse_payment_message(yandex_money_data.valid_body2)
        self.assertEqual(transaction.payer, 'nc2232')
        self.assertEqual(transaction.sum, u'895.52')

    def test_parse_invalid_body(self):
        self.assertIsNone(self.provider.parse_payment_message(u'<div></div>'))


class TestYandexMoneyProccess(unittest.TestCase):
    def setUp(self):
        self.provider = yandex_money.YandexMoney()

    @mock.patch.object(yandex_money.YandexMoney, 'get_payments')
    @mock.patch.object(base_transaction.BaseTransaction, 'process')
    def test_simple(self, payment_process_mock, get_payments_mock):
        get_payments_mock.return_value = [
            base_transaction.BaseTransaction(None, None, '10', 'payer1'),
            base_transaction.BaseTransaction(None, None, '10', 'payer4'),
        ]
        self.provider.process()
        self.assertEqual(payment_process_mock.call_count, 2)

    def test_sum(self):
        trans = base_transaction.BaseTransaction(None, None, u'611 руб. 20 коп.', 'test_payer')
        self.assertEqual(trans.sum, u'611.20')
