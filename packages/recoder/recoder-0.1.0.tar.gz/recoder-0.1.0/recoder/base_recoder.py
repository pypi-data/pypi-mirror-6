# -*- coding: utf-8 -*-

from __future__ import with_statement
import json

__all__ = ['BaseRecoder']


class BaseRecoder(object):
    base_dir = None
    file_3grams = None
    file_plus_words = None
    codings = None

    funcs = ['encode', 'decode']

    def __init__(self, depth=2, errors='ignore', use_plus_words=False):
        self.depth = depth
        self.errors = errors
        self.use_plus_words = use_plus_words
        self.operation_chain = None

        with open(self.file_3grams) as f:
            self.grams = json.load(f)

        with open(self.file_plus_words) as f:
            self.plus_words = set(json.load(f))

    def _contains_plus_word(self, text):
        for word in self.plus_words:
            if (u' ' + word + u' ') in text:
                return True
        return False

    def _iter(self, text, depth, chain=[]):
        if depth <= 0:
            raise StopIteration
        for coding in self.codings:
            for func in self.funcs:
                try:
                    fixed_text = getattr(text, func)(coding, errors=self.errors)
                    operation = {'func': func, 'coding': coding}
                    next_chain = chain + [operation]
                    yield fixed_text, next_chain
                    for sub_fixed_text, sub_chain in self._iter(fixed_text, depth - 1, next_chain):
                        yield sub_fixed_text, sub_chain
                except UnicodeError:
                    pass

    def _calc_weight(self, text):
        weight = 0.0
        count = 0
        for i in xrange(len(text) - 2):
            gram = text[i:i+3]
            weight += self.grams.get(gram, 0.0)
            count += 1
        return (weight / count) if count else 0.0

    def fix(self, unicode_text):
        max_weight = self._calc_weight(unicode_text.lower())
        max_text = unicode_text
        for fixed_text, operation_chain in self._iter(unicode_text, self.depth):
            if not isinstance(fixed_text, unicode):
                continue
            fixed_text = fixed_text.lower()
            weight = self._calc_weight(fixed_text.lower())
            if weight > max_weight and (not self.use_plus_words or self._contains_plus_word(fixed_text)):
                max_weight = weight
                self.operation_chain = operation_chain
                max_text = unicode_text
                for item in operation_chain:
                    max_text = getattr(max_text, item['func'])(item['coding'], errors=self.errors)
        return max_text

    def fix_common(self, unicode_text):
        max_weight = self._calc_weight(unicode_text.lower())
        max_text = unicode_text

        for ce in self.codings:
            for cd in self.codings:
                if ce == cd: continue
                try:
                    fixed_text = unicode_text.encode(ce, errors=self.errors).decode(cd, errors=self.errors).lower()
                    weight = self._calc_weight(fixed_text)
                    if weight > max_weight and (not self.use_plus_words or self._contains_plus_word(fixed_text)):
                        max_weight = weight
                        max_text = unicode_text.encode(ce, errors=self.errors).decode(cd, errors=self.errors)
                        self.operation_chain = [
                            {'func': 'encode', 'coding': ce},
                            {'func': 'decode', 'coding': cd}
                        ]
                except UnicodeError:
                    pass
        return max_text
