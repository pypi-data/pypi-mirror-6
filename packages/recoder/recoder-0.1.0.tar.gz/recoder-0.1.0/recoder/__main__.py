# -*- coding: utf-8 -*-

import sys
import cyrillic

coding = sys.argv[1] if len(sys.argv) > 1 else 'utf-8'
input_data = sys.stdin.read().decode(coding, errors='ignore')
output_data = cyrillic.Recoder().fix_common(input_data).encode(coding, errors='ignore')
sys.stdout.write(output_data)
sys.stdout.flush()