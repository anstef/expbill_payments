# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

from logger import success_logger


class BaseProvider(object):
    def __init__(self):
        pass

    def get_payments(self):
        raise NotImplementedError()

    def _process(self):
        payments = self.get_payments()
        has_valid_payments = False
        for payment in payments:
            if not has_valid_payments:
                has_valid_payments = True

            payment.process()

        if not has_valid_payments:
            success_logger.info('There are no new payments')