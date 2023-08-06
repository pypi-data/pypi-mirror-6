# -*- coding: utf-8 -*-

from __future__ import with_statement

from .pyver import *
import json

__all__ = ['BaseRecoder']

html_parser = HTMLParser.HTMLParser()

class BaseRecoder(object):
    base_dir = None
    file_3grams = None
    file_plus_words = None
    codings = None

    funcs = [
        [lambda *args, **kwargs: kwargs['text'].encode(kwargs['coding'], errors=kwargs['errors']), True, (unicode_type,)],
        [lambda *args, **kwargs: kwargs['text'].decode(kwargs['coding'], errors=kwargs['errors']), True, (encoded_type,)],
        [lambda *args, **kwargs: unquote_plus(kwargs['text']), False, (encoded_type,)],
        [lambda *args, **kwargs: unquote_plus(kwargs['text'].replace('=', '%')), False, (encoded_type,)],
        [lambda *args, **kwargs: html_parser.unescape(kwargs['text']), False, (unicode_type,)],
    ]

    regular_error_classes = (
        UnicodeError,
        AttributeError,  # for py3 support
    )

    def __init__(self, depth=2, errors='ignore', use_plus_words=False):
        self.depth = depth
        self.errors = errors
        self.use_plus_words = use_plus_words
        self.last_transform = None

        with open(self.file_3grams) as f:
            self.grams = json.load(f)

        with open(self.file_plus_words) as f:
            self.plus_words = set(json.load(f))

    def _contains_plus_word(self, text):
        for word in self.plus_words:
            if (' ' + word + ' ') in text:
                return True
        return False

    def _iter(self, text, depth, transform=lambda _text: _text):
        if depth <= 0:
            raise StopIteration
        for func, coding_dependent, allowed_types in self.funcs:
            if not isinstance(text, allowed_types): continue
            for coding in (self.codings if coding_dependent else ['fake_coding']):
                try:
                    fixed_text = func(text=text, coding=coding, errors=self.errors)
                    new_transform = lambda _text: func(text=transform(_text), coding=coding, errors=self.errors)
                    yield fixed_text, new_transform
                    for sub_fixed_text, sub_new_transform in self._iter(fixed_text, depth - 1, new_transform):
                        yield sub_fixed_text, sub_new_transform
                except self.regular_error_classes:
                    pass

    def _calc_weight(self, text):
        weight = 0.0
        count = 0

        for i in range_iterator(len(text) - 2):
            gram = text[i:i+3]
            weight += self.grams.get(gram, 0.0)
            count += 1
        return (weight / count) if count else 0.0

    def fix(self, unicode_text):
        max_weight = self._calc_weight(unicode_text.lower())
        max_text = unicode_text
        for fixed_text, transform in self._iter(unicode_text, self.depth):
            if not isinstance(fixed_text, unicode_type):
                continue
            fixed_text = fixed_text.lower()
            weight = self._calc_weight(fixed_text)
            if weight > max_weight and (not self.use_plus_words or self._contains_plus_word(fixed_text)):
                max_weight = weight
                max_text = transform(unicode_text)
                self.last_transform = transform
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
                        self.last_transform = lambda text: text.encode(ce, errors=self.errors).decode(cd, errors=self.errors)
                except self.regular_error_classes:
                    pass
        return max_text
