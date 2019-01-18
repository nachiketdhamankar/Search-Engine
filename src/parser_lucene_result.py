# -*- coding: utf-8 -*-
from collections import defaultdict
import utils
import os
import json

def lucene_result_parser():
	result_set = defaultdict(list)
	result_path = os.path.join(utils.RESULT_DIR, "lucene_regular")
	files = os.listdir(result_path)

	for file in files:
		qid, ext = os.path.basename(file).split(".")
		file_path = os.path.join(result_path, file)
		if ext == "txt":
			with open(file_path, "r") as fp:
				content = fp.read().split("\n")
				for row in content:
					if len(row) > 0:
						doc_path, score = row.split()
						_, score = score.split("=")
						docid = os.path.basename(doc_path).split(".")[0]
						result_set[qid].append((docid, float(score)))

	result_path = os.path.join(utils.RESULT_DIR, "lucene", "stem_False_stop_False_lucene_score.csv")
	result_path2 = os.path.join(utils.RESULT_DIR, "lucene", "stem_False_stop_False_lucene_score.json")
	utils.write(None, result_path, result_set, csvf=True)
	utils.write(None, result_path2, result_set)

lucene_result_parser()