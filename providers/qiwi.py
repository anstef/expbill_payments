# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import json
import sqlite3

import requests
from BeautifulSoup import BeautifulSoup
import settings
from logger import success_logger, error_logger
from providers.base_provider import BaseProvider
from transactions.base_transaction import BaseTransaction


class QiwiProcessException(Exception):
    pass


class Qiwi(BaseProvider):
    def __init__(self):
        super(Qiwi, self).__init__()
        self.conn = sqlite3.connect(settings.db_name)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS transactions (trans_id TEXT)")
        #self.cur.execute("DELETE FROM transactions")

    def process(self):
        try:
            success_logger.info("Start processing")
            self._process()
        except QiwiProcessException, e:
            error_logger.error(e)
        except Exception, e:
            error_logger.exception(e)
        finally:
            self.close_db_conn()
            success_logger.info("Stop processing")

    def get_payments(self):
        try:
            payments_page = self.get_last_payments_page()
        except requests.ConnectionError:
            raise QiwiProcessException(u"Can't request qiwi URL")

        return self.parse_payments_page(payments_page)

    def parse_payments_page(self, body):
        transactions = []

        for payment in BeautifulSoup(body).findAll('div', {'class': 'reportsLine status_SUCCESS'}):
            sum = payment.find('div', {'class': 'originalExpense'}, recursive=False).span.string
            trans_id = payment.find('div', {'class': 'DateWithTransaction'}, recursive=False).div.string
            payer_div = payment.find('div', {'class': 'ProvWithComment'}, recursive=False)
            comment = payer_div.find('div', {'class': 'provider'}, recursive=False).text
            payer = payer_div.find('div', {'class': 'comment'}, recursive=False).string

            transaction = BaseTransaction(self.cur, trans_id, sum, payer, comment, 'QIWI')
            if transaction.trans_id and not transaction.is_processed():
                transactions.append(transaction)

        return transactions

    def get_last_payments_page(self):
        s = requests.Session()

        pimary_auth = s.post(
            settings.qiwi_login_url,
            data={'source': 'MENU', 'login': settings.qiwi_login, 'password': settings.qiwi_pass},
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json, text/javascript, */*; q=0.01'})

        if pimary_auth.status_code != 200:
            raise QiwiProcessException(u'Primary auth fail. Status code: %s' % pimary_auth.status_code)

        try:
            pimary_auth_res = json.loads(pimary_auth.text)
            token = pimary_auth_res['data']['token']
        except ValueError:
            raise QiwiProcessException(u'Invalid auth response: %s' % pimary_auth.text)
        except KeyError:
            raise QiwiProcessException(u'Invalid auth response: %s' % pimary_auth.text)

        token_auth = s.post(settings.qiwi_login_url,
               data={'source': 'MENU', 'login': settings.qiwi_login, 'password': settings.qiwi_pass, 'loginToken': token},
               headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json, text/javascript, */*; q=0.01'})

        if pimary_auth.status_code != 200:
            raise QiwiProcessException(u'Token auth fail. Status code: %s' % token_auth.status_code)

        payments = s.get(settings.qiwi_payments_url)
        if payments.status_code != 200:
            raise QiwiProcessException(u'Get payments page fail. Status code: %s' % payments.status_code)

        return payments.text

    def close_db_conn(self):
        self.conn.commit()
        self.conn.close()
