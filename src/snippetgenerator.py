# -*- coding: utf-8 -*-
from collections import defaultdict
from bs4 import BeautifulSoup as bs
import argparse
import logging
import utils
import json
import nltk
import math
import os


NON_SIG_WORDS = 4


class SnippetGenerator(object):
	def __init__(self, args, scores, queries, index):
		self.log = utils.get_logger("Snippet Generator")
		self.scores = scores
		self.queries = queries
		self.index = index

		self.snippets = defaultdict(list)
		self.query_doc_sent = defaultdict(dict)

		if args.debug:
			self.log.setLevel(logging.DEBUG)

	def generate_snippets(self):
		for qid, scores in self.scores.items():
			self.snippets[qid] = self._generate_snippets(qid, scores)
			# break

	def _generate_snippets(self, qid, scores):
		self.log.info(qid)
		self.log.info("Snippets for \'{}\'".format(self.queries[qid]))
		doc_snippets = []
		for res in scores:
			docid, _ = res
			sentence_list = self.get_sentences(docid)
			sentence, score = self.calc_luhn_score(qid, docid, sentence_list, self.get_doc_vocab(docid))
			sentence = self.highlight(sentence, self.queries[qid])

			self.log.info("{}==>{}==>{}".format(docid, sentence, score))
			doc_snippets.append((docid, sentence))

			# break
		return doc_snippets

	def highlight(self, sentence, query):
		# self.log.debug(sentence)
		# self.log.debug(query)
		query_tokens = set(query.split())
		sentence_tokens = sentence.split()
		for i in range(len(sentence_tokens)):
			word = sentence_tokens[i]
			if word in query_tokens:
				sentence_tokens[i] = "**{}**".format(word)

		return " ".join(sentence_tokens)

	def calc_luhn_score(self, qid, docid, sentence_list, vocab):

		def find_window(sentence, sig_words):
			i = 0
			j = len(sentence)-1

			while i < j:
				window = sentence[i:j]
				total_words_in_window = len(window)
				sig_words_in_window = len(sig_words.intersection(window))

				non_sig_words = total_words_in_window - sig_words_in_window
				if non_sig_words <= NON_SIG_WORDS:
					return len(window)
				i += 1

			return 0
	
		sentence_scores = []
		sd = len(sentence_list)

		# get list of significant words for this document using luhn's empirical formula
		sig_words = set(filter(lambda w: self.issignificant(w, sd, docid), vocab))

		for each_sentence in sentence_list:
			sentence_sig_word_count = len(set(each_sentence).intersection(sig_words))
			window_length = find_window(each_sentence, sig_words)
			sentence_score = ((math.pow(sentence_sig_word_count, 2)/window_length) or 0)
			sentence_scores.append((each_sentence, sentence_score))

		sentence_scores = sorted(sentence_scores, key=lambda x: x[1], reverse=True)
		return sentence_scores[0]

	def issignificant(self, w, sd, docid):
		fd = self.get_word_count_in_doc(w, docid)
		return ((sd < 25 and fd >= (7 - 0.1*(25-sd))) or 
				(sd >= 25 and sd <= 40 and fd >= 7) or
				(fd >= (7 + 0.1*(sd-40))))

	def get_word_count_in_doc(self, w, docid):
		try:
			for entry in self.index[w]:
				if entry[0] == docid:
					return entry[1]
		except KeyError:
			return 0

	def get_sentences(self, docid):
		"""Given a docid, returns the list of sentences in the document

		Args:
			docid (String)

		Returns:
			(List)
		"""
		html_file = os.path.join(utils.DATA_DIR, "cacm", "{}.html".format(docid))

		with open(html_file, "r") as fp:
			soup = bs(fp.read(), "html.parser")
			content = soup.find('pre').get_text()
			content = content.replace("\n", " ")
			try:
				pm_index = content.index("pm")
				content = content[:pm_index+1]
			except ValueError:
				pass

			return nltk.sent_tokenize(content.lower())

	def get_doc_vocab(self, docid):
		"""Given a docid, returns the vocab list

		Args:
			docid (String)

		Returns:
			(Set)
		"""
		corpus_file = os.path.join(utils.CORPUS_DIR, "{}.txt".format(docid))
		with open(corpus_file, "r") as fp:
			return set(fp.read().split())



def main(args):
	scores = defaultdict(list)
	queries = defaultdict(str)
	index_file = "stem_False_stop_False_inverted_index.txt"
	index = utils.load_inverted_index(os.path.join(utils.INDEX_DIR, index_file))

	results_path = os.path.join(utils.RESULT_DIR, args.file)
	with open(results_path, 'r') as fp:
		scores = json.loads(fp.read())

	queries = utils.load_query_map()
	obj = SnippetGenerator(args, scores, queries, index)
	obj.generate_snippets()

	file_path = os.path.join(utils.RESULT_DIR, "snippet_generation.csv")
	utils.write(obj.log, file_path, obj.snippets, csvf=True)


if __name__ == '__main__':
	parser = argparse.ArgumentParser("SnippetGenerator")

	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument("-m", "--model", default="", type=str)
	parser.add_argument("-f", "--file", default="", type=str)

	args = parser.parse_args()
	main(args)