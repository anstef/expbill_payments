# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import requests
import re
import settings
from logger import success_logger, error_logger


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


class BaseTransaction(object):
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
        if self.cursor:
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