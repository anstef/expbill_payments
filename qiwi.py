# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import requests
import json
import re
import logging
from BeautifulSoup import BeautifulSoup
import sqlite3
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import settings


formatter = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
current_dir = os.path.dirname(os.path.abspath(__file__))

error_logger = logging.getLogger('failed_payment')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(os.path.join(current_dir, 'fail.log'))
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

success_logger = logging.getLogger('success_payments')
success_logger.setLevel(logging.INFO)
success_handler = logging.FileHandler(os.path.join(current_dir, 'success.log'))
success_handler.setFormatter(formatter)
success_handler.setLevel(logging.INFO)
success_logger.addHandler(success_handler)


def send_email(subject, message):
    try:
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.email_from, settings.email_from_pass)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, 'utf-8')
        msg.attach(MIMEText(message.encode('utf-8'), 'html', 'UTF-8'))
        server.sendmail(settings.email_from, settings.email_to, msg.as_string())
    except Exception, e:
        error_logger.exception(e)


class QiwiProcessException(Exception):
    pass


class PaymentTransaction(object):
    REPLACE_CYRILIC_MAP = {
        u'а': u'a',
        u'б': u'b',
        u'в': u'b',
        u'д': u'd',
        u'е': u'e',
        u'к': u'k',
        u'л': u'l',
        u'м': u'm',
        u'н': u'n',
        u'о': u'o',
        u'р': u'p',
        u'с': u'c',
        u'т': u't',
        u'х': u'x',
        u'ю': u'u',
    }

    def __init__(self, cursor, trans_id, sum_raw, payer, comment=None):
        self.cursor = cursor
        self.trans_id = trans_id
        if sum_raw:
            self.sum = sum_raw.replace(u'руб.', '').replace(',', '.')
            self.sum = re.sub('[^\d\.]', '', self.sum)
        else:
            self.sum = None
        self.payer = payer.strip() if payer else ''
        self._replace_cyrilic_from_payer()

        self.comment = comment

    def _replace_cyrilic_from_payer(self):
        for cyrilic_letter, latin_letter in self.REPLACE_CYRILIC_MAP.iteritems():
            if cyrilic_letter in self.payer:
                self.payer = self.payer.replace(cyrilic_letter, latin_letter)

    def is_processed(self):
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE trans_id=%s" % self.trans_id)
        return self.cursor.fetchone()[0]

    def process(self):
        self.save()
        self.cursor.execute("INSERT INTO transactions VALUES(%s)" % self.trans_id)

    def save(self):
        if not self.payer:
            msg = u"Can't create billing transaction for empty payer id=%s, sum=%s." % (self.trans_id, self.sum)
            error_logger.error(msg)
            send_email(u'BAD empty payer %s руб.' % self.sum, msg)
            return

        res = self.create_billing_payment(self.payer)

        if res.status_code == 200 and res.text == '-1':
            res = self.create_billing_payment(re.sub('[^\w-]', '', self.payer))

        if res.status_code == 200 and res.text == '-1':
            res = self.create_billing_payment(re.sub('[^\d-]', '', self.payer))

        if res.status_code == 200 and res.text == '0':
            msg = u'Billing payment sucessfull created - transaction_id, sum, payer, comments: %s' % [self.trans_id, self.sum, self.payer, self.comment]
            success_logger.info(msg)
            send_email(u'OK %s %s руб.' % (self.payer, self.sum), msg)
        else:
            msg = u"Can't create billing transaction id=%s, payer=%s, sum=%s. Http status: %s" % \
                  (self.trans_id, self.payer, self.sum, res.status_code)
            if res.text == '-1':
                msg += u'\nNo such payer in billing'
            send_email(u'BAD %s %s руб.' % (self.payer, self.sum), msg)
            msg += u'\nresponse text: %s'% res.text
            error_logger.error(msg)

    def create_billing_payment(self, payer):
        return requests.get(
            settings.billing_payment_url,
            params={'sum': self.sum, 'uid': payer, 'trans': self.trans_id, 'secret': settings.billing_secret})


class Qiwi(object):
    def __init__(self):
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

    def _process(self):
        payments = self.get_payments()
        has_valid_payments = False
        for payment in payments:
            if not payment.trans_id or payment.is_processed():
                continue
            elif not has_valid_payments:
                has_valid_payments = True

            payment.process()

        if not has_valid_payments:
            success_logger.info('There are no new payments with transaction id')

    def get_payments(self):
        try:
            payments_page = self.get_last_payments_page()
        except requests.ConnectionError:
            raise QiwiProcessException(u"Can't request qiwi URL")

        return self.parse_payments_page(payments_page)

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

    def parse_payments_page(self, body):
        payments = []

        for payment in BeautifulSoup(body).findAll('div', {'class': 'reportsLine status_SUCCESS'}):
            sum = payment.find('div', {'class': 'originalExpense'}, recursive=False).span.string
            trans_id = payment.find('div', {'class': 'DateWithTransaction'}, recursive=False).div.string
            payer_div = payment.find('div', {'class': 'ProvWithComment'}, recursive=False)
            comment = payer_div.find('div', {'class': 'provider'}, recursive=False).text
            payer = payer_div.find('div', {'class': 'comment'}, recursive=False).string

            payments.append(PaymentTransaction(self.cur, trans_id, sum, payer, comment))

        return payments

    def close_db_conn(self):
        self.conn.commit()
        self.conn.close()
