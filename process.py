# -*- coding: utf-8 -*-
# Author: Andrey Ovchinnikov anstef42@gmail.com

from providers.qiwi import Qiwi
from providers.yandex_money import YandexMoney
from providers.osmp import Osmp

Qiwi().process()
YandexMoney().process()
Osmp().process()
