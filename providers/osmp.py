# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import imaplib
import email

import settings
from logger import success_logger, error_logger
from providers.base_provider import BaseProvider
from transactions.base_transaction import BaseTransaction


class OsmpProcessException(Exception):
    pass


class Osmp(BaseProvider):
    provider_name = 'osmp'

    def process(self):
        try:
            success_logger.info("Start processing")
            self._process()
        except OsmpProcessException, e:
            error_logger.error(e)
        except Exception, e:
            error_logger.exception(e)
        finally:
            success_logger.info("Stop processing")

    def get_payments(self):
        self._mail_connect()
        unread_messages = self._get_unread()

        if not unread_messages:
            return []

        transactions = []
        for e_id in unread_messages.split():
            message_transactions = self.parse_payment_message(self._get_attachment_text(e_id))
            if message_transactions:
                transactions += message_transactions

        return transactions

    def parse_payment_message(self, body):
        payments_lines = body.strip().split('\r\n')[1:-1]
        payments = []
        for payment_line in payments_lines:
            payment = payment_line.split('\t')
            payments.append(BaseTransaction(None, None, payment[4], payment[3], None, 'OSMP'))

        return payments

    def _mail_connect(self):
        self.mail_conn = imaplib.IMAP4_SSL(settings.osmp_mail_server, settings.osmp_mail_port)
        self.mail_conn.login(settings.osmp_mail_login, settings.osmp_mail_pass)
        self.mail_conn.select('INBOX')

    def _get_unread(self):
        status, response = self.mail_conn.search(None, '(UNSEEN FROM "%s")' % settings.osmp_sender_mail)
        if status != 'OK':
            raise OsmpProcessException(u"Can't get unread messages. Status: %s" % status)

        return response[0]

    def _get_attachment_text(self, e_id):
        _, response = self.mail_conn.fetch(e_id, '(RFC822)')
        message = email.message_from_string(response[0][1])
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                if filename is not None:
                    return part.get_payload(decode=True)

        return None