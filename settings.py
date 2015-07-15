# -*- coding: utf-8 -*-

db_name = '/tmp/payments.db'

#qiwi
qiwi_login_url = 'https://auth.qiwi.com/cas/tgts'
qiwi_payments_url = 'https://visa.qiwi.com/report/list.action?type=1'
qiwi_login = 'login'
qiwi_pass = 'pass'

#yandex money
ym_mail_server = 'imap.yandex.ru'
ym_mail_port = '993'
ym_mail_login = 'your-notification-mail@yandex.ru'
ym_mail_pass = 'q123'

#billing
billing_payment_url = 'http://yourbilling.com/payments.simpleterminal/simpleterminal/payment/'
billing_secret = '123456'

#email
email_from = 'robot@yoursite.com'
email_from_pass = 'q123'
email_to = 'admin@yoursite.com'
smtp_server = 'smtp.gmail.com'
smtp_port = '587'

from local_settings import *