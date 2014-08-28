Payment loader to ExpertBilling

Features:
-----

 * Load payments from Qiwi with simple parsing daily payments HTML-page.
 * The successfully processed transaction will not duplicated in billing script restarting

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
