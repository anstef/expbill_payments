# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

from logger import success_logger, error_logger


class BaseProvider(object):
    provider_name = 'base'
    def __init__(self):
        pass

    def get_payments(self):
        raise NotImplementedError()

    def process(self):
        self._log_start()
        try:
            self._process()
        except Exception, e:
            error_logger.exception(e)
        finally:
            self._log_stop()

    def _process(self):
        payments = self.get_payments()
        has_valid_payments = False
        for payment in payments:
            if not has_valid_payments:
                has_valid_payments = True

            payment.process()

        if not has_valid_payments:
            success_logger.info('There are no %s new payments' % self.provider_name)

    def _log_start(self):
        success_logger.info("Start %s processing" % self.provider_name)

    def _log_stop(self):
        success_logger.info("Stop %s processing" % self.provider_name)