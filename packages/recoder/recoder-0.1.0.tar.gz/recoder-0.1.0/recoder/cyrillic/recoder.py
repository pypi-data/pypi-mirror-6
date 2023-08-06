# -*- coding: utf-8 -*-

import os
from ..base_recoder import BaseRecoder

__all__ = ['Recoder']


class Recoder(BaseRecoder):
    base_dir = os.path.dirname(__file__)
    file_3grams = os.path.join(base_dir, '3grams.json')
    file_plus_words = os.path.join(base_dir, 'plus_words.json')

    codings = [
        'utf-8',
        'koi8-r',
        'koi8-u',
        'cp1251',
        'cp1252',
        'iso8859-1',
        'iso8859-2',
        'iso8859-5',
        'iso8859-9',
        'cp866',
        'maccyrillic'
    ]