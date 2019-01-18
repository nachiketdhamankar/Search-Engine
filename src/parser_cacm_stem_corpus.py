# -*- coding: utf-8 -*-
import utils
import os
import re

r = re.compile("\s[a|p]m\s")

def parse_stem_corpus():
	with open(os.path.join(utils.BASE_DIR, "data", "cacm_stem.txt"), "r") as fp:
		content = fp.read()
		corpii = content.split("#")
		print(len(corpii))
		for t in corpii[1:]:
			y = t.split()
			# print(t)
			zeroes = 4 - len(y[0])
			doc_id = 'CACM-{}{}.txt'.format('0'*zeroes, y[0])
			filename = os.path.join(utils.BASE_DIR, "data", "stem_corpus", doc_id)
			z = ' '.join(y[1:])
			try:
				z, _ = r.split(z)
				z += " pm"
			except ValueError:
				pass
			with open(filename, "w") as fwp:
				fwp.write(z)

parse_stem_corpus()