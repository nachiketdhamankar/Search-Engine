# -*- coding: utf-8 -*-
from nltk import sent_tokenize, word_tokenize
from bs4 import BeautifulSoup as bs
import utils
import os
import re
import logging
import argparse

PCH = r"""!#$%&()*+/:;<=>?@[\]^_'"`{|}~,.-'"""
R = re.compile("\s[a|p]m\s")

class Parser(object):
	"""Parses html documents and generates a cleaned file after
	1. Stemming
	2. Case folding
	3. Stopping
	"""
	def __init__(self, args):
		self.log = utils.get_logger("ParserLog")

		if args.debug:
			self.log.setLevel(logging.DEBUG)

	def parse(self):
		"""Wrapper to parse html files to text files
		"""
		self.log.info("Cleaning corpus")
		corpus_path = os.path.join(utils.DATA_DIR, "cacm")
		files = os.listdir(corpus_path)
		files = list(map(lambda x: os.path.join(corpus_path, x), files))

		for file in files:
			self._parse(file)

	def _parse(self, fpath):
		"""Parses the HTML document at input file path into a simple text file
		with content

		Arguments:
			fpath (String) - File Path
		"""
		file_name, ext = os.path.basename(fpath).split(".")
		corpus_file_path = os.path.join(utils.CORPUS_DIR, "{}.txt".format(file_name))

		if ext == "html":
			with open(fpath, 'r') as fp:
				soup = bs(fp.read(), "html.parser")
				content = soup.find('pre').get_text()
				if args.casefolding:
					content = content.lower()

				try:
					content, _ = R.split(content)
					content = content + " pm"
				except ValueError:
					pass

				content = self.clean(content)
				# concat all terms with a single space character
				content = " ".join(content)

				self.log.debug(corpus_file_path)
				with open(corpus_file_path, 'w') as fwp:
					fwp.write(content)

	def clean(self, content):
		"""Removes special character from the content

		Arguments:
			content (String)
		"""
		tokens_list=[]

		def remove_special_chars(token):
			for p in PCH:
				if token.startswith(p):
					return False
			return not token in PCH

		def remove_fullstop_end(token):
			if token.endswith('.'):
				return token[:-1]
			return token

		sentences = sent_tokenize(content)
		
		for sentence in sentences:
			tokens = word_tokenize(sentence)
			tokens = filter(remove_special_chars, tokens)
			tokens = map(remove_fullstop_end, tokens)
			tokens = filter(lambda x: x, tokens)
			tokens_list.extend(tokens)
		
		# content = re.sub("[',\"^(){};/<>*!@#$%.+=|-?~:]+", " ", content)
		return tokens_list


def main(args):
	print(args)
	obj = Parser(args)
	obj.parse()

if __name__ == "__main__":
	utils.check_dirs()

	parser = argparse.ArgumentParser(
		description="Parse arguments for parser")
	
	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument('-case', '--casefolding', action='store_true')
	parser.add_argument('-stem', '--stemming', action='store_true')
	parser.add_argument('-stop', '--stopping', action='store_true')
	parser.add_argument('-stopf', '--stopwordsfile', default="", type=str)

	args = parser.parse_args()
	main(args)