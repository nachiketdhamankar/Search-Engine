import utils
from jmsmoothing import JelinekMercer
from tfidf import TFiDF
from bm25 import BM25
import os
import nltk
import logging
import argparse
import pandas as pd
from operator import add, sub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RELEVANT_DOC_COUNT = 15
PCH = r"""!#$%&()*+/:;<=>?@[\]^_'"`{|}~,.-'"""
ALPHA = 1
BETA = 0.75
GAMMA = 0.15

list_queries = utils.load_queries(utils.PARSED_QUERIES)
inverted_index = utils.load_inverted_index(os.path.join(utils.INDEX_DIR, "stem_False_stop_False_inverted_index.txt"))
# args = {debug: False, isstemmed: False, isstopped: False}

parser = argparse.ArgumentParser(description="Parser for JM Smoothing")
	
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument("-stem", "--isstemmed", action="store_true")
parser.add_argument("-stop", "--isstopped", action="store_true")

args = parser.parse_args()

baseline_run = BM25(args, inverted_index,
					 utils.load_corpus_stats(), list_queries)
# dict query_id: [[doc_name,score],[],[] ....]
baseline_run.compute_scores()
results = baseline_run.bm25_scores
query_mapping = utils.load_query_map()


def get_content(doc_names):
	doc_contents = []
	for doc in doc_names:
		with open(os.path.join(utils.CORPUS_DIR, "{}.txt".format(doc)), "r") as f:
			doc_contents.append(f.read())
	return doc_contents


def vocabularize(corpus_string):
	tokens = nltk.tokenize.word_tokenize(corpus_string)
	vocabulary = {}
	for token in tokens:
		if token in vocabulary:
			vocabulary[token] += 1
		else:
			vocabulary[token] = 1
	return vocabulary.keys()


def get_vocabulary(doc_content):
	# tokens = nltk.tokenize.word_tokenize(doc_content)
	# tokens = filter(remove_special_chars,tokens)
	corpus = " ".join(doc_content)
	corpus_tokens = corpus.split()
	return list(set(corpus_tokens))


def get_vector(data, vocab):
	dimension = len(vocab)
	vector = [0] * dimension
	data = data.split()
	for token in data:
		try:
			position = vocab.index(token)
			vector[position] += 1
		except ValueError:
			logger.error("{} does not exist in vocabulary".format(token))
			pass
	return vector


def get_query_terms(query_id):
	return query_mapping[query_id]


def remove_special_chars(token):
	for p in PCH:
		if token.startswith(p):
			return False
	return not token in PCH


def get_query_tokens(query_terms):
	tokens = nltk.tokenize.word_tokenize(query_terms)
	tokens = filter(remove_special_chars, tokens)
	return tokens


def rocchio(query_vector, rel_vectors, non_rel_vectors):
	sum_rel_vectors = list(map(sum, zip(*rel_doc_vectors)))
	sum_rel_vectors = map(lambda x: x * BETA / len(rel_vectors), sum_rel_vectors)
	sum_non_rel_vectors = list(map(sum, zip(*non_rel_doc_vectors)))
	sum_non_rel_vectors = map(lambda x: GAMMA * x / len(non_rel_vectors), sum_non_rel_vectors)
	query_vector = map(lambda x: x * ALPHA, query_vector)
	query_rel_vector = list(map(add, query_vector, sum_rel_vectors))
	new_query_vector = list(map(sub, query_rel_vector, sum_non_rel_vectors))
	return new_query_vector


def get_query(vocab, vector):
	# print(vector)
	query = ""
	for position, weight in enumerate(vector):
		if weight > 0.1:
			query = query + " " + vocab[position]
	return query


modified_queries = []
for query_id, docs in results.items():
	# relevant_docs = docs[:RELEVANT_DOC_COUNT]
	doc_names = list(map(lambda x: x[0], docs))
	doc_contents = get_content(doc_names)  # return list of strings
	# vocabulary = get_vocabulary(doc_contents)
	vocabulary = list(inverted_index.keys())
	query_string = get_query_terms(query_id)
	query_tokens = query_string.split()
	# import pdb; pdb.set_trace()
	temp = set(vocabulary).union(set(query_tokens))
	vocabulary = [i for i in temp]
	# print(query_string)
	# query_tokens = get_query_tokens(query_terms)
	query_vector = get_vector(query_string, vocabulary)
	df = pd.DataFrame(doc_contents, columns=['document'])
	df['doc_vector'] = df['document'].apply(get_vector, args=(vocabulary,))
	doc_vectors = df['doc_vector'].tolist()
	rel_doc_vectors = doc_vectors[:RELEVANT_DOC_COUNT]
	non_rel_doc_vectors = doc_vectors[RELEVANT_DOC_COUNT:]
	modified_query_vector = rocchio(query_vector, rel_doc_vectors, non_rel_doc_vectors)
	modified_query = get_query(vocabulary, modified_query_vector)
	modified_queries.append(modified_query)

logger.info("Second Run Starting...")


obj = BM25(args, inverted_index, utils.load_corpus_stats(), modified_queries)
obj.compute_scores()

result_path = os.path.join(utils.RESULT_DIR, "query_enrichment_bm25.json")
utils.write(None, result_path, obj.bm25_scores)
result_path2 = os.path.join(utils.RESULT_DIR, "query_enrichment_bm25.csv")
utils.write(None, result_path2, obj.bm25_scores, csvf=True)


