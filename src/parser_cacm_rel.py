# -*- coding: utf-8 -*-
from collections import defaultdict
import utils
import os
import json

def parse_rel_docs():
	result = defaultdict(list)

	rel_docs = os.path.join(utils.BASE_DIR, "data", "cacm.rel.txt")
	with open(rel_docs, "r") as fp:
		content = fp.read().split('\n')
		for row in content:
			if len(row) > 0:
				id, _, docid, _ = row.split()
				qid = "Q{}".format(int(id)-1)
			result[qid].append(docid)

	file_path = os.path.join(utils.BASE_DIR, "data", "cacm.parsed.rel.txt")
	utils.write(None, file_path,result)

parse_rel_docs()