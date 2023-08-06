# -*- coding: utf-8 -*-

import regex

class Builder(object):
    def __init__(self, plus_words_count=30, grams_count=10000):
        self.plus_words_count = plus_words_count
        self.grams_count = grams_count

    def build_grams(self, unicode_text):
        unicode_text = unicode_text.lower()
        grams = {}
        for i in xrange(len(unicode_text) - 2):
            gram = unicode_text[i:i+3]
            grams[gram] = grams.get(gram, 0) + 1
        top_grams = sorted(grams.iteritems(), key=lambda item: item[1], reverse=True)[:self.grams_count]
        return dict(top_grams)

    def build_plus_words(self, unicode_text):
        unicode_text = unicode_text.lower()
        unicode_text = regex.sub(u'\W', u' ', unicode_text, regex.U)
        unicode_text = regex.sub(u'[\d_]', u' ', unicode_text, regex.U)
        unicode_text = regex.sub(u'\s+', u' ', unicode_text, regex.U).strip()
        plus_words = {}
        for words in regex.split(u'\s+', unicode_text):
            plus_words[words] = plus_words.get(words, 0) + 1
        top_words = sorted(plus_words.iteritems(), key=lambda item: item[1], reverse=True)[:self.plus_words_count]
        return dict(top_words).keys()