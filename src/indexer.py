# -*- coding: utf-8 -*-
from collections import defaultdict
import utils
import os
import json
import logging
import argparse


class Indexer(object):
	def __init__(self, corpus_path, args):
		self.corpus_name = corpus_path
		self.log = utils.get_logger("IndexerLog")
		self.inverted_index = defaultdict(list)
		self.positional_index = defaultdict(list)
		self.corpus_stats = defaultdict(dict)
		self.corpus = defaultdict(str)

		self.stopped_words = None
		self.isstopped = args.isstopped
		if args.debug:
			self.log.setLevel(logging.DEBUG)

	def read(self):
		"""Read the corpus directory into memory
		"""
		files = os.listdir(self.corpus_name)
		files = list(map(lambda x: os.path.join(self.corpus_name, x), files))

		for file in files:
			docid, ext = os.path.basename(file).split(".")
			if ext == "txt":
				with open(file, 'r', encoding='utf-8') as fp:
					content = fp.read()
					self.corpus[docid] = content.split()

	def index(self):
		"""Wrapper to create inverted index
		"""
		self.log.info("Creating Inverted Index")

		if self.isstopped:
			self.read_stopped_words()

		for docid, content in self.corpus.items():
			self._index(docid, content)

		self.log.debug("{}".format(self.inverted_index.keys()))

	def _index(self, docid, content):
		"""Indexer
		
		Arguments:
			docid (String)
			content (String)
		"""
		self.log.debug("{}, Words: {}".format(docid, len(content)))
		
		vocab = set(content)
		term_freq = list(map(lambda x: content.count(x), vocab))

		for word, freq in zip(vocab, term_freq):
			if self.isstopped and word in self.stopped_words:
				continue
			self.inverted_index[word].append((docid, freq))

	def create_positional_index(self):
		"""Wrapper to create positional index
		"""
		self.log.info("Creating Positional Indexes")

		for docid, content in self.corpus.items():
			vocab = set(content)
			words = content
			self._create_positional_index(docid, vocab, words)

	def _create_positional_index(self, docid, vocab, words):
		for w in vocab:
			j = 0
			pos_index = []
			start_index = words.index(w)
			for i in range(start_index, len(words)):
				if words[i] == w:
					# if j == 0:
					pos_index.append(i)
					# else:
					# 	pos_index.append(i-pos_index[j-1])
					# j += 1

			if len(pos_index) > 0:
				self.positional_index[w].append((docid, pos_index))

	def create_corpus_stats(self):
		for docid, content in self.corpus.items():
			self.corpus_stats[docid] = {
				"word_count": len(content),
				"unique_words": len(set(content))
			}

	def read_stopped_words(self):
		with open(os.path.join(utils.BASE_DIR, "data", "common_words"), "r") as fp:
			self.stopped_words = set(fp.read().split("\n"))


def main(args):
	print(args)
	obj = None

	if args.isstemmed:
		obj = Indexer(utils.STEM_CORPUS_DIR, args)
	else:
		obj = Indexer(utils.CORPUS_DIR, args)
	
	obj.read()
	
	# create inverted indexes
	obj.index()
	file_name = "stem_{}_stop_{}_inverted_index.txt".format(args.isstemmed, args.isstopped)
	file_path = os.path.join(utils.INDEX_DIR, file_name)
	utils.write(obj.log, file_path, obj.inverted_index)
	
	# create positional indexes
	obj.create_positional_index()
	file_name = "stem_{}_stop_{}_positional_index.txt".format(args.isstemmed, args.isstopped)
	file_path = os.path.join(utils.INDEX_DIR, file_name)
	utils.write(obj.log, file_path, obj.positional_index)

	# create corpus stats
	obj.create_corpus_stats()
	file_name = "stem_{}_stop_{}_corpus_stats.txt".format(args.isstemmed, args.isstopped)
	file_path = os.path.join(utils.INDEX_DIR, file_name)
	utils.write(obj.log, file_path, obj.corpus_stats)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description="Parse arguments for Indexer")
	
	parser.add_argument('-d', '--debug', action="store_true")
	parser.add_argument('-stem', '--isstemmed', action="store_true")
	parser.add_argument('-stop', '--isstopped', action="store_true")
	main(parser.parse_args())
