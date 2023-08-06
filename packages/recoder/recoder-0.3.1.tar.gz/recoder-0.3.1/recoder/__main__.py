# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
from . import cyrillic
from .pyver import *

coding = sys.argv[1] if len(sys.argv) > 1 else 'utf-8'

if pyver == 2:
    input_data = sys.stdin.read().decode(coding, errors='ignore')
elif pyver == 3:
    if len(sys.argv) == 1:
        input_data = sys.stdin.read()
    else:
        input_data = sys.stdin.buffer.read().decode(coding, errors='ignore')

output_data = cyrillic.Recoder().fix_common(input_data)

if pyver == 2:
    sys.stdout.write(output_data.encode(coding, errors='ignore'))
elif pyver == 3:
    if len(sys.argv) == 1:
        sys.stdout.write(output_data)
    else:
        sys.stdout.buffer.write(output_data.encode(coding, errors='ignore'))
