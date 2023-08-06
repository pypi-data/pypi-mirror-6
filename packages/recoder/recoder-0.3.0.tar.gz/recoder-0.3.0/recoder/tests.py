# -*- coding: utf-8 -*-

import unittest
from recoder import cyrillic
from recoder.pyver import *

class TestMain(unittest.TestCase):
    if pyver == 2:
        sample_text = 'какой-то текст для примера работы библиотеки'.decode('utf-8')
    elif pyver == 3:
        sample_text = 'какой-то текст для примера работы библиотеки'

    cyr_recoder = cyrillic.Recoder()

    def test_cyrillic_cp1251_koi8r(self):
        self.assertEqual(self.sample_text, self.cyr_recoder.fix_common(self.sample_text.encode('cp1251').decode('koi8-r')))

    def test_cyrillic_cp1251_iso8859_9(self):
        self.assertEqual(self.sample_text, self.cyr_recoder.fix_common(self.sample_text.encode('cp1251').decode('iso8859-9')))
