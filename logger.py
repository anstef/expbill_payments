# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

import os
import logging

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