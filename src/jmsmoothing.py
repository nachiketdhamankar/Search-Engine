# -*- coding: utf-8 -*-
from collections import defaultdict
from model import RetrievalModel
from functools import reduce
import argparse
import math


class JelinekMercer(RetrievalModel):
	def __init__(self, args):
		super().__init__(args, "JM-Smoothing")
		self.L = args.lambdaval
		self.C = 0

	def compute_query_doc_score(self, query, docid):
		D = self.corpusStats[docid]["word_count"]
		doc_score = 0

		for term in query:
			if (not self.isStopped) or (self.isStopped and word not in self.stopWords):
				try:
					word_index = self.invertedIndex[term]
					temp = list(filter(lambda x: x[0]==docid, word_index))
					fqid = temp[0][1] if len(temp) > 0 else 0
					cqi = reduce(lambda x, y: x+y[1], word_index, 0)

					A = ((1-self.L)*(fqid/D))
					B = (self.L*(cqi/self.C))

					doc_score += math.log(A+B)
				except ZeroDivisionError:
					self.log.warning("A and B = 0 for {} in {}".format(term, docid))
					pass
				except KeyError:
					# self.log.warning("Missing key {}".format(term))
					pass
		return (docid, doc_score)

	def compute_corpus_size(self):
		corpus_stats = self.corpusStats.values()
		self.C = reduce(lambda x, y: x+y["word_count"], corpus_stats, 0)

def main(args):
	print(args)

	model = JelinekMercer(args)
	model.load_data()
	model.compute_corpus_size()
	model.compute_scores()
	model.output()

if __name__ == '__main__':
	parser = argparse.ArgumentParser("JM-Smoothing")

	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument('-o', "--output", help="Output format [CSV, JSON]", default="json", type=str)
	parser.add_argument('-m', "--maxDocs", help="Number of output documents per query", default=100, type=int)
	parser.add_argument('-L', "--lambdaval", help="Lambda value for JM-Smoothing", type=float, required=True)
	parser.add_argument('-stem', "--isStemmed", help="Set if stemming is performed", action="store_true", required=False)
	parser.add_argument('-stop', "--isStopped", help="Set if stopping is performed", action="store_true", required=False)
	args = parser.parse_args()

	main(args)
