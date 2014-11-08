# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import json
import imaplib

import requests
from BeautifulSoup import BeautifulSoup
import settings
from logger import success_logger, error_logger
from providers.base_provider import BaseProvider
from transactions.base_transaction import BaseTransaction


class YandexMoneyProcessException(Exception):
    pass


class YandexMoney(BaseProvider):
    def process(self):
        try:
            success_logger.info("Start processing")
            self._process()
        except YandexMoneyProcessException, e:
            error_logger.error(e)
        except Exception, e:
            error_logger.exception(e)
        finally:
            success_logger.info("Stop processing")

    def get_payments(self):
        try:
            payments_page = self.get_payment_html()
        except requests.ConnectionError:
            raise YandexMoneyProcessException(u"Can't request qiwi URL")

        return self.parse_payments_page(payments_page)

    def get_payment_html(self):
        pass

    def parse_payments_page(self, body):
        payments = []

        for payment in BeautifulSoup(body).findAll('div', {'class': 'reportsLine status_SUCCESS'}):
            sum = payment.find('div', {'class': 'originalExpense'}, recursive=False).span.string
            trans_id = payment.find('div', {'class': 'DateWithTransaction'}, recursive=False).div.string
            payer_div = payment.find('div', {'class': 'ProvWithComment'}, recursive=False)
            comment = payer_div.find('div', {'class': 'provider'}, recursive=False).text
            payer = payer_div.find('div', {'class': 'comment'}, recursive=False).string

            payments.append(BaseTransaction(None, None, sum, payer, comment))

        return payments
