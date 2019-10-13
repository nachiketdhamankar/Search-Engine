from collections import defaultdict
import utils
import os


def create_query_map():
	queries = utils.load_queries(utils.PARSED_QUERIES)
	res = defaultdict(str)
	for i in range(len(queries)):
		qid = "Q{}".format(i)
		res[qid] = queries[i]

	file_path = os.path.join(utils.DATA_DIR, "query.parsed.map.txt")
	utils.write(None, file_path, res)

create_query_map()