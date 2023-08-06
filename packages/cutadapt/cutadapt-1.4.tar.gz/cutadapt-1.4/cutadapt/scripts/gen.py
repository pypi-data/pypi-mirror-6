#!/usr/bin/env python3

import sys
import random

from ..seqio import FastqReader

adapter = 'GCCTAACTTCTTAGACTGCCTTAAGGACGT'

with FastqReader(sys.stdin) as fr:
	for r in fr:
		l = len(r)
		pos = random.randint(0, 2*l)
		print(pos, file=sys.stderr)
		newseq = r.sequence[0:pos] + adapter + r.sequence[pos:]
		# cut to original length
		newseq = newseq[:l]
		r.sequence = newseq
		if pos < l:
			r.name += ' adapter start: {0}'.format(pos)
		print(r)
