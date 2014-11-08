Payment loader to ExpertBilling

Features:
-----

 * Loads payments from Qiwi with simple parsing daily payments HTML-page.
 * Loads payments from Yandex Money by parsing unread notification messages from email.
 * The successfully processed transaction don't duplicate when billing script restarts.

Usage:
-----

0. install dependencies
  `pip install -r requirements.txt`
1. define settings in local_settings.py
2. run the tests
  `python -m unittest -v tests`
3. run
  `python ./process.py`
4. Check logs in success.log and fail.log
