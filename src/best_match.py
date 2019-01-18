def get_inverted_index(term):
	return corpus_index[term]

def best_match(query):
	qcorpus_index = utils.load_inverted_index(os.path.join(utils.INDEX_DIR,"stem_False_stop_False_inverted_index.txt")) 
	# query = "tss operating system"
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