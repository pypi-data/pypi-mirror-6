# -*- coding: utf-8 -*-

import sys
from recoder import cyrillic
from recoder.pyver import *

coding = sys.argv[1] if len(sys.argv) > 1 else 'utf-8'

if pyver == 2:
    input_data = sys.stdin.read().decode(coding, errors='ignore')
elif pyver == 3:
    input_data = sys.stdin.buffer.read().decode(coding, errors='ignore')

output_data = cyrillic.Recoder().fix_common(input_data).encode(coding, errors='ignore')

if pyver == 2:
    sys.stdout.write(output_data)
elif pyver == 3:
    sys.stdout.buffer.write(output_data)
