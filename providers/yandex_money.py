# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import imaplib
import email

from BeautifulSoup import BeautifulSoup
import settings
from logger import success_logger, error_logger
from providers.base_provider import BaseProvider
from transactions.base_transaction import BaseTransaction


class YandexMoneyProcessException(Exception):
    pass


class YandexMoney(BaseProvider):
    provider_name = 'ym'
    def process(self):
        try:
            success_logger.info("Start %s processing" % self.provider_name)
            self._process()
        except YandexMoneyProcessException, e:
            error_logger.error(e)
        except Exception, e:
            error_logger.exception(e)
        finally:
            success_logger.info("Stop %s processing" % self.provider_name)

    def get_payments(self):
        self._mail_connect()
        unread_messages = self._get_unread()

        if not unread_messages:
            return []

        transactions = []
        for e_id in unread_messages.split():
            transaction = self.parse_payment_message(self._get_msg_body(e_id))
            if transaction:
                transactions.append(transaction)

        return transactions

    def parse_payment_message(self, body):
        if BeautifulSoup(body).find(text=u'Деньги успешно зачислены') or \
                BeautifulSoup(body).find(text=u'Перевод от другого пользователя'):
            sum = BeautifulSoup(body).find(text=u'Сумма').previous.previous.nextSibling.contents[0].text
            payer = BeautifulSoup(body).find(text=u'Комментарий').previous.previous.nextSibling.contents[0].text

            return BaseTransaction(None, None, sum.replace(u'&nbsp;', ''), payer, None, 'YM')

        return None

    def _mail_connect(self):
        self.mail_conn = imaplib.IMAP4_SSL(settings.ym_mail_server, settings.ym_mail_port)
        self.mail_conn.login(settings.ym_mail_login, settings.ym_mail_pass)
        self.mail_conn.select('INBOX')

    def _get_unread(self):
        status, response = self.mail_conn.search(None, '(UNSEEN HEADER SENDER "%s")' % settings.ym_sender_mail)
        if status != 'OK':
            raise YandexMoneyProcessException(u"Can't get unread messages. Status: %s" % status)

        return response[0]

    def _get_msg_body(self, e_id):
        _, response = self.mail_conn.fetch(e_id, '(RFC822)')
        return email.message_from_string(response[0][1]).get_payload().decode("quoted-printable")
