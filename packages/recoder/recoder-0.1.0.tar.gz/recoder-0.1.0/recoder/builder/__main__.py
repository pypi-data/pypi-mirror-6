# -*- coding: utf-8 -*-

from __future__ import with_statement

import sys
import json
from .builder import Builder

coding = sys.argv[1] if len(sys.argv) > 1 else 'utf-8'
input_data = sys.stdin.read().decode(coding, errors='ignore')
builder = Builder()

with open('3grams.json', 'w') as f:
    grams = builder.build_grams(input_data)
    json.dump(grams, f, indent=4)

with open('plus_words.json', 'w') as f:
    plus_words = builder.build_plus_words(input_data)
    json.dump(plus_words, f, indent=4)