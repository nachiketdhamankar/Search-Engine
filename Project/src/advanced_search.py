import utils
import os
import argparse
import json

corpus_index = utils.load_inverted_index(os.path.join(utils.INDEX_DIR,"stem_False_stop_False_positional_index.txt")) 

def get_inverted_index(term):
	return corpus_index[term]

def best_match(query):
	qcorpus_index = utils.load_inverted_index(os.path.join(utils.INDEX_DIR,"stem_False_stop_False_inverted_index.txt")) 
	query_terms = query.split()
	inverted_list_all_terms = []
	for term in query_terms:
		inverted_list_all_terms.extend(get_inverted_index(term))

	doc_relevance = {}
	for docid_positions in inverted_list_all_terms:
		if docid_positions[0] in doc_relevance:
			doc_relevance[docid_positions[0]] += 1
		else:
			doc_relevance[docid_positions[0]] = 1

	doc_relevance_list = zip(doc_relevance.keys(),doc_relevance.values())

	return sorted(doc_relevance_list, key=lambda x: x[1], reverse=True)

def get_relevance_count(position_lists_all_docs, comparator, n):
	first = position_lists_all_docs[0]
	for i in range(1, len(position_lists_all_docs)):
		second = position_lists_all_docs[i]
		first_i = 0
		second_j = 0
		new_l = []
		while first_i < len(first) and second_j < len(second):
			if comparator(first[first_i], second[second_j], n):#first[first_i] + 1 == second[second_j]:
				new_l.append(second[second_j])
				first_i += 1
				second_j += 1
			elif first[first_i] < second[second_j]:
				first_i += 1
			elif first[first_i] > second[second_j]:
				second_j += 1

		if first_i < len(first) and i == 0:
			for index in range(first_i, len(first)):
				new_l.append(first[index])
		first = new_l

	return len(first)


def exact_comparator(a, b, N=0):
	return a + 1 == b


def order_n_comparator(a, b, N):
	return a < b <= (a + 1 + N)


def extact_match_wrapper(comparator,query,n):
	query_terms = query.split()
	inverted_list_all_terms = []
	for term in query_terms:
		print(term)
		inverted_list_all_terms.append(get_inverted_index(term))

	docids = set(map(lambda x: x[0], inverted_list_all_terms[0]))
	for i in range(1, len(inverted_list_all_terms)):
		temp = set(map(lambda x: x[0], inverted_list_all_terms[i]))

		docids = docids.intersection(temp)

	common_docs = list(docids)

	doc_relevance = []
	for doc in common_docs:
		doc_lists = []
		for inverted_list_term in inverted_list_all_terms:
			temp = list(filter(lambda x: x[0] == doc, inverted_list_term))

			doc_lists.append(temp[0][1])
		x = (doc, get_relevance_count(doc_lists, comparator, n))
		doc_relevance.append(x)

	return sorted(doc_relevance, key=lambda x: x[1], reverse=True)


def main(args):
	print(args)
	if args.exactmatch:
		return extact_match_wrapper(exact_comparator,args.query, args.proximitymatch)
	elif args.proximitymatch:
		return extact_match_wrapper(order_n_comparator,args.query,args.proximitymatch)
	elif args.bestmatch:
		return best_match(args.query)


if __name__ == "__main__":
	parser = argparse.ArgumentParser("TF-IDF ArgumentParser")
	

	parser.add_argument("-d", "--debug", action="store_true")
	parser.add_argument('-e', "--exactmatch", action="store_true")
	parser.add_argument('-b', "--bestmatch", action="store_true")
	parser.add_argument('-n', "--proximitymatch", default=0, type=int)
	parser.add_argument('-q', "--query", default="", type=str)

	args = parser.parse_args()
	print(main(args))