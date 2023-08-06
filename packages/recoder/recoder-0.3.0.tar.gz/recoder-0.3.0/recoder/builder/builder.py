# -*- coding: utf-8 -*-

from recoder.pyver import *
import regex

class Builder(object):
    def __init__(self, plus_words_count=30, grams_count=10000):
        self.plus_words_count = plus_words_count
        self.grams_count = grams_count

    def build_grams(self, unicode_text):
        unicode_text = unicode_text.lower()
        grams = {}
        for i in range_iterator(len(unicode_text) - 2):
            gram = unicode_text[i:i+3]
            grams[gram] = grams.get(gram, 0) + 1
        top_grams = sorted(grams.items(), key=lambda item: item[1], reverse=True)[:self.grams_count]
        return dict(top_grams)

    def build_plus_words(self, unicode_text):
        unicode_text = unicode_text.lower()

        if pyver == 2:
            unicode_text = regex.sub('\W'.decode('utf-8'), ' '.decode('utf-8'), unicode_text, regex.U)
            unicode_text = regex.sub('[\d_]'.decode('utf-8'), ' '.decode('utf-8'), unicode_text, regex.U)
            unicode_text = regex.sub('\s+'.decode('utf-8'), ' '.decode('utf-8'), unicode_text, regex.U).strip()
            words = regex.split('\s+'.decode('utf-8'), unicode_text)
        elif pyver == 3:
            unicode_text = regex.sub('\W', ' ', unicode_text, regex.U)
            unicode_text = regex.sub('[\d_]', ' ', unicode_text, regex.U)
            unicode_text = regex.sub('\s+', ' ', unicode_text, regex.U).strip()
            words = regex.split('\s+', unicode_text)

        plus_words = {}
        for word in words:
            plus_words[word] = plus_words.get(word, 0) + 1
        top_words = sorted(plus_words.items(), key=lambda item: item[1], reverse=True)[:self.plus_words_count]
        return dict(top_words).keys()