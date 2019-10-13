# -*- coding: utf-8 -*-
from collections import defaultdict
from matplotlib import pyplot as plt
import argparse
import logging
import utils
import json
import csv
import os


class Query(object):
	def __init__(self, qid, retrieved_docs, B):
		self.qid = qid
		self.retrieved_docs = retrieved_docs
		self.rel_docs = None
		self.precision_values = []
		self.recall_values = []
		self.A = None
		self.B = B
		self.p5 = None
		self.p20 = None
		self.precision = None
		self.recall = None


class Evaluation(object):
	def __init__(self, model, file, rel_docs):
		self.log = utils.get_logger("Evaluation")
		self.model = model
		self.ranks_file_path = os.path.join(utils.RESULT_DIR, file)
		self.rel_docs = rel_docs
		self.queries = defaultdict(Query)

	def filter_queries(self):
		self.log.info("Filtering non relevant queries")
		query_ids = set(self.rel_docs.keys())
		all_query_ids = set(self.queries.keys())

		remove_qids = all_query_ids - query_ids
		for qid in remove_qids:
			del self.queries[qid]

	def populate_query_data(self):
		self.log.info("Populating Query Data")
		query_ids = set(self.rel_docs.keys())
		for qid in query_ids:
			qobj = self.queries[qid]
			qobj.rel_docs = set(self.rel_docs[qid])
			qobj.A = len(self.rel_docs[qid])
			self.calc_precision_recall(qobj)

	def create_queries(self):
		with open(self.ranks_file_path, "r") as fp:
			content = json.loads(fp.read())
			for qid, vals in content.items():
				docs = [x[0] for x in vals]
				self.queries[qid] = Query(qid, docs, len(docs))

	def calc_ap_rr(self, qobj):
		"""Calculate AP and RR values given a query object

		Returns:
			(float, float) - (AP, RR)
		"""
		rel_docs = qobj.rel_docs

		rr = 0
		rr_flag = True
		pre_vals = []
		try:
			for i in range(len(qobj.retrieved_docs)):
				# import pdb; pdb.set_trace()
				docid = qobj.retrieved_docs[i]
				prec = qobj.precision_values[i]
				if docid in rel_docs:
					if rr_flag:
						rr = float(1.0/(i+1))
						rr_flag = False
					pre_vals.append(prec)
			ap = sum(pre_vals)*1.0/(1.0*len(pre_vals))
			self.log.debug("{}-AP={}".format(qobj.qid, ap))
			return ap, rr
		except ZeroDivisionError:
			return 0, rr

	def calc_map_mrr(self):
		"""Calculate MAP and MRR values
		"""
		self.log.info("Calculate MAP and MRR")

		all_aps_rrs = []
		for q in self.queries.values():
			all_aps_rrs.append(self.calc_ap_rr(q))

		mrr_val = map_val = 0
		for val in all_aps_rrs:
			map_val += val[0]
			mrr_val += val[1]

		map_val = float(map_val/len(all_aps_rrs))
		mrr_val = float(mrr_val/len(all_aps_rrs))

		self.log.info("MAP={}, MRR={}".format(map_val, mrr_val))

		return map_val, mrr_val

	def calc_p_at_k(self):
		self.log.info("Populating P@K, Final Precision and Recall values")
		for qid, _ in self.queries.items():
			self.queries[qid].p5 = self.queries[qid].precision_values[4]
			self.queries[qid].p20 = self.queries[qid].precision_values[19]
			# self.queries[qid].precision = self.queries[qid].precision_values[-1:][0]
			# self.queries[qid].recall = self.queries[qid].recall_values[-1:][0]

	def calc_precision_recall(self, query):
		"""
		"""
		self.log.info("Calculate all Precision/Recall for {}".format(query.qid))
		rank = 1
		for i in range(query.B):
			if query.retrieved_docs[i] in query.rel_docs:
				rank += 1
			query.precision_values.append(float(rank/(i+1)))
			query.recall_values.append(float(rank/query.A))


	def get_stats(self, map_val, mrr_val):
		def get_query_stats(qobj):
			packet = {
				"QID": qobj.qid,
				"P@5": qobj.p5,
				"P@20": qobj.p20,
				"Final_Precision": qobj.precision_values[-1:][0],
				"Final_Recall": qobj.recall_values[-1:][0],
			}

			return packet

		qids = self.queries.keys()
		result = {
			"MAP": map_val,
			"MRR": mrr_val,
			"Stats": list(map(lambda qid: get_query_stats(self.queries[qid]), qids))
		}

		return result

	def get_pr_graph(self, model):
		p = []
		QUERY_COUNT = 64
		fixed_recall_values = [float(i/20) for i in range(20)]

		for _, qobj in self.queries.items():
			p.append(self.interpolate(qobj.precision_values, qobj.recall_values, fixed_recall_values))

		final_p = list(map(sum, zip(*p)))
		final_p = list(map(lambda x: float(x/QUERY_COUNT), final_p))
		
		return (fixed_recall_values, final_p)

	def create_pr_files(self):
		path = os.path.join(utils.RESULT_DIR,  "PR_{}.csv".format(self.model))
		with open(path, 'w') as fp:
			writer = csv.writer(fp)
			for qid, qobj in self.queries.items():
				writer.writerow(["Q{}".format(qid), "Precision and Recall Values"])
				arr1 = ["Precision"]
				arr2 = ["Recall"]

				arr1.extend(qobj.precision_values)
				arr2.extend(qobj.recall_values)
			
				writer.writerow(arr1)
				writer.writerow(arr2)

				writer.writerow([])
				writer.writerow([])
				
	def create_p_at_k_files(self):
		path = os.path.join(utils.RESULT_DIR,  "P@K_{}.csv".format(self.model))
		with open(path, 'w') as fp:
			writer = csv.writer(fp)
			writer.writerow(["QID", "P@5", "P@20"])
			writer.writerow([])

			for qid, qobj in self.queries.items():
				arr1 = ["Q{}".format(qid), qobj.p5, qobj.p20]
				writer.writerow(arr1)

	def interpolate(self, precision, query_recall, recall):

		def get_next_recall_index(temp):
			for i in range(len(query_recall)):
				if query_recall[i] >= temp:
					return temp

		def get_prec_at_index(idx):
			i = idx-1
			j = idx+1

			while i >= 0 and j < len(precision):
				if precision[i] == precision[j]:
					i -= 1
					j += 1
				else:
					return max(precision[i], precision[j])

		precision_result = []
		for fixed_recall in recall:
			if fixed_recall in set(recall):
				idx = recall.index(fixed_recall)
				precision_result.append(precision[idx])
			else:
				idx = get_next_recall_index(fixed_recall)
				precision_result.append(get_prec_at_index(idx))

		return precision_result

def create_graph(result):
	img_path = os.path.join(utils.RESULT_DIR, "PLOT.png")

	fig, ax = plt.subplots()
	ax.set_title("Precision Recall Graph")
	ax.set_xlabel("Recall")
	ax.set_ylabel("Precision")
	ax.set_xlim([0.0, 1.0])
	ax.set_ylim([0.0, 1.0])

	model = result[0]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='r', label=model[0])
	
	model = result[1]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='g', label=model[0])	

	model = result[2]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='b', label=model[0])

	model = result[3]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='r', label=model[0])

	model = result[4]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='y', label=model[0])

	model = result[5]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='m', label=model[0])

	model = result[6]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='c', label=model[0])

	model = result[7]
	recall = model[1][0]
	precision = model[1][1]
	ax.plot(recall, precision, alpha=0.5, color='k', label=model[0])
	
	legend = ax.legend(loc='upper right', shadow=True)
	legend.get_frame().set_facecolor('#FFFFFF')
	fig.savefig(img_path, figsize=(12,8))

def load_rel_docs():
	with open(os.path.join(utils.DATA_DIR, "cacm.parsed.rel.txt"), "r") as fp:
		content = json.loads(fp.read())
		return content

def main(model, filename):
	rel_docs = load_rel_docs()
	obj = Evaluation(model, filename, rel_docs)
	obj.create_queries()

	obj.log.debug("Initiated Queries = {}".format(len(obj.queries)))
	obj.filter_queries()
	obj.log.debug("Relevance Feedback Queries = {}".format(len(obj.queries)))
	obj.populate_query_data()

	map_val, mrr_val = obj.calc_map_mrr()
	obj.calc_p_at_k()

	file_path = os.path.join(utils.RESULT_DIR, "eval_{}.txt".format(obj.model))
	utils.write(obj.log, file_path, obj.get_stats(map_val, mrr_val))

	obj.create_pr_files()
	obj.create_p_at_k_files()
	return obj.get_pr_graph(model)

if __name__ == '__main__':
	plots = {
		"stem_False_stop_False_lucene_score.txt": "lucene",
		"stem_False_stop_False_jm_score.json": "jm",
		"stem_False_stop_True_jm_score.json": "jm_stop",
		"stem_False_stop_False_tfidf_score.json": "tfidf",
		"stem_False_stop_True_tfidf_score.json": "tfidf_stop",
		"stem_False_stop_False_bm25_score.json": "bm25",
		"stem_False_stop_True_bm25_score.json": "bm25_stop",
		"query_enrichment_bm25.json": "bm25_enrich",
	}

	plot_params = []

	for filename, model in plots.items():
		plot_params.append((model, main(model, filename)))
	# print(plot_params)
	create_graph(plot_params)