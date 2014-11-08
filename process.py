# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

from providers.qiwi import Qiwi
from providers.yandex_money import YandexMoney

Qiwi().process()
YandexMoney().process()
