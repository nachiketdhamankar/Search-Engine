# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import utils
import os
import re

PCH = r"""!#$%&()*+/:;<=>?@[\]^_'"`{|}~,.-'"""

def parse_cacm_queries():
	queries = []
	with open(os.path.join(utils.DATA_DIR, "cacm.query.txt"), "r") as fp:
		soup = bs(fp.read(), 'html.parser')
		res = soup.find_all('doc')
		qmap = defaultdict(str)
		for x in res:
			s = x.text
			text = s.split()
			qid = text[0]
			qry = " ".join(text[1:])
			qry = re.sub("[,\"^(){};/<>*'!@#$%.+=|?`~:]+", "", qry)
			queries.append(qry.lower())

	print("No of queries {}".format(len(queries)))
	with open(os.path.join(utils.DATA_DIR, "cacm.parsed.query.txt"), "w") as fp:
		fp.write('\n'.join(queries))



parse_cacm_queries()