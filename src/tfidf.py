# -*- coding: utf-8 -*-
from model import RetrievalModel
import argparse
import math


N = 3204


class TFIDF(RetrievalModel):
	def __init__(self, args):
		super().__init__(cmdargs=args, model="TFIDF")

	def compute_query_doc_score(self, query, docid):
		doc_score = 0
		for word in query:
			if (not self.isStopped) or (self.isStopped and word not in self.stopWords):
				try:
					iidx_word = self.invertedIndex[word]
					temp = list(filter(lambda x: x[0]==docid, iidx_word))
					tf = temp[0][1] if len(temp) > 0 else 0
					nk = len(iidx_word)
					idf = math.log(N/nk)
					doc_score += float(tf*idf)
				except KeyError:
					pass
		return (docid, doc_score)


def main(args):
	print(args)
	model = TFIDF(args)
	model.load_data()
	model.compute_scores()
	model.output()

if __name__ == '__main__':
	parser = argparse.ArgumentParser("TF-IDF")

	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument('-o', "--output", help="Output format [CSV, JSON]", default="json", type=str)
	parser.add_argument('-m', "--maxDocs", help="Number of output documents per query", default=100, type=int)
	parser.add_argument('-stem', "--isStemmed", help="Set if stemming is performed", action="store_true", required=False)
	parser.add_argument('-stop', "--isStopped", help="Set if stopping is performed", action="store_true", required=False)
	args = parser.parse_args()

	main(args)
