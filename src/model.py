from collections import defaultdict
import logging
import utils
import json
import csv
import os


class RetrievalModel(object):
	"""BaseClass for Implmenting Retrieval Models
	"""

	def __init__(self, cmdargs, model):
		self.invertedIndex = None
		self.queries = None
		self.corpusStats = None
		self.stopWords = None
		self.model = model

		# Command Line options
		self.isStopped = cmdargs.isStopped
		self.isStemmed = cmdargs.isStemmed
		self.maxDocs = cmdargs.maxDocs
		self.outputType = cmdargs.output

		self.scores = defaultdict(list)
		self.log = utils.get_logger(model)

		if cmdargs.debug:
			self.log.setLevel(logging.DEBUG)

	def compute_query_doc_score(self, query, docid):
		"""
		Args:
			query (list): List of Query Terms
			docid (str):  Doc ID for the document

		Returns:
			list((docid, score), ...): List of tuples of docid and its scores
		"""
		pass

	def compute_scores(self):
		"""Wrapper to compute scores for all queries in the input queries
		"""
		docids = self.corpusStats.keys()
		for qid, query in self.queries.items():
			self.log.info("Calculating Query Score: {}".format(qid))
			self.scores[qid] = self._compute_score(qid, query, docids)
		self.sort_results()

	def _compute_score(self, qid, query, docids):
		"""Compute for the given query id and query for all documents
		"""
		query = query.split()
		scores = list(map(lambda docid: self.compute_query_doc_score(query, docid),
						   docids))
		return scores

	def sort_results(self):
		for qid, scores in self.scores.items():
			self.scores[qid] = sorted(
				scores, key=lambda x: x[1], reverse=True)[:self.maxDocs]

	def load_data(self):
		self._load_inverted_index()
		self._load_queries()
		self._load_corpus_stats()
		self._load_stop_words()

	def _load_inverted_index(self):
		file_name = "stem_{}_stop_{}_inverted_index.txt".format(
			self.isStemmed, self.isStopped)
		file_path = os.path.join(utils.INDEX_DIR, file_name)
		fp = open(file_path, 'r')
		self.invertedIndex = json.loads(fp.read())
		fp.close()

	def _load_queries(self):
		file_path = utils.PARSED_QUERIES
		if self.isStemmed:
			file_path = utils.STEM_QUERIES

		fp = open(file_path, "r")
		self.queries = json.loads(fp.read())
		fp.close()

	def _load_corpus_stats(self):
		file_name = "stem_False_stop_{}_corpus_stats.txt".format(
			self.isStopped)
		file_path = os.path.join(utils.INDEX_DIR, file_name)
		fp = open(file_path, 'r')
		self.corpusStats = json.loads(fp.read())
		fp.close()

	def _load_stop_words(self):
		file_path = os.path.join(utils.BASE_DIR, "data", "common_words")
		with open(file_path, "r") as fp:
			stopwords = fp.read().split("\n")
		if stopwords[-1:] == "":
			self.stopwords = stopwords[:-1]
		self.stopwords = set(stopwords)

	def output(self):
		if self.outputType == "csv":
			self._output_to_csv()
		else:
			self._output_to_json()

	def _output_to_json(self):
		file_name = "stem_{}_stop_{}_{}.json".format(
			self.isStemmed, self.isStopped, self.model)
		file_path = os.path.join(utils.RESULT_DIR, file_name)
		fp = open(file_path, 'w')
		fp.write(json.dumps(self.scores))
		fp.close()

	def _output_to_csv(self):
		file_name = "stem_{}_stop_{}_{}.csv".format(self.isStemmed,
													self.isStopped, self.model)
		file_path = os.path.join(utils.RESULT_DIR, file_name)
		fp = open(file_path, 'w')
		writer = csv.writer(fp)
		writer.writerow(["Query ID", "Document ID", "Score"])
		for qid, scores in self.scores.items():
			for (docid, score) in scores:
				writer.writerow([qid, docid, score])

		fp.close()
