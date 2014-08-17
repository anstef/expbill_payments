# -*- coding: utf-8 -*-

db_name = '/tmp/payments.db'

#qiwi
qiwi_login_url = 'https://visa.qiwi.com/auth/login.action'
qiwi_payments_url = 'https://visa.qiwi.com/report/list.action?type=1'
qiwi_login = 'login'
qiwi_pass = 'pass'

#billing
billing_payment_url = 'http://yourbilling.com/payments.simpleterminal/simpleterminal/payment/'
billing_secret = '123456'

#email
email_from = 'robot@yoursite.com'
email_from_pass = 'q123'
email_to = 'admin@yoursite.com'
smtp_server = 'smtp.gmail.com'
smtp_port = '587'