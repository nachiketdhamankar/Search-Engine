# -*- coding: utf-8 -*-
from model import RetrievalModel
from functools import reduce
import argparse
import utils
import math


class BM25(RetrievalModel):
	def __init__(self, args):
		super().__init__(args, "BM25")
		self.avdl = 0

	def _compute_term_score(self, term, ni, fi, dl, qfi):

		N = utils.N
		k1 = 1.2
		k2 = 100
		b = 0.75
		R = 0.0
		r = 0.0
		K = k1*((1-b) + (b*(dl/self.avdl)))

		A = ((r + 0.5)/(R - r + 0.5))/((ni - r + 0.5)/(N - ni - R + r + 0.5))
		logA = math.log(A)
		B = ((k1 + 1)*fi)/(K + fi)
		C = ((k2 + 1)*qfi)/(k2 + qfi)

		score = logA*B*C
		return score

	def compute_query_doc_score(self, query, docid):
		doc_score = 0
		for term in query:
			if (not self.isStopped) or (self.isStopped and word not in self.stopWords):
				ni = 0 if term in self.invertedIndex else len(self.invertedIndex[term])
				temp = [] if term in self.invertedIndex else list(filter(lambda x: x[0]==docid, self.invertedIndex[term]))
				fi = temp[0][1] if len(temp) > 0 else 0
				doc_score += self._compute_term_score(term, ni, fi, self.corpusStats[docid]["word_count"], query.count(term))
		return (docid, doc_score)

	def precompute_avdl(self):
		corpus_stats = self.corpusStats.values()
		corpus_size = reduce(lambda x, y: x+y["word_count"], corpus_stats, 0)
		self.avdl = float(corpus_size/len(corpus_stats))


def main(args):
	print(args)

	model = BM25(args)
	model.load_data()
	model.precompute_avdl()
	model.compute_scores()
	model.output()

if __name__ == '__main__':
	parser = argparse.ArgumentParser("BM25")

	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument('-o', "--output", help="Output format [CSV, JSON]", default="json", type=str)
	parser.add_argument('-m', "--maxDocs", help="Number of output documents per query", default=100, type=int)
	parser.add_argument('-stem', "--isStemmed", help="Set if stemming is performed", action="store_true", required=False)
	parser.add_argument('-stop', "--isStopped", help="Set if stopping is performed", action="store_true", required=False)
	args = parser.parse_args()

	main(args)
