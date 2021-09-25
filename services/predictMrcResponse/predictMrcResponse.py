import falcon
import requests
import json
import configparser

from db.functions.Corpus import Corpus
from db.functions.CorpusFiles import CorpusFiles


class PredictMrcResponse():
	def __init__(self):
		# self.corpus_name = ''
		# self.question = ''
		config = configparser.ConfigParser()
		config.read('./services/Config.ini')
		self.get_context_url = config['ServicesConfig']['get_context_url']
		self.predict_response_url = config['ServicesConfig']['predict_response_url']

		self.id_separator = '<==>'
		self.mrc_corpus_features_url = config['ServicesConfig']['mrc_corpus_features_url']
	# endDef

	def on_post(self, req, resp):
		question_json = json.load(req.bounded_stream,encoding='utf-8')
		corpus_name = question_json['corpus_name']
		question = question_json['question']

		top_k_context = 1
		if question_json.get('top_k_context'):
			top_k_context = int(question_json.get('top_k_context'))

		corpus = Corpus()
		corpus_details = corpus.get_corpus_details_by_name(corpus_name)

		model_name = corpus_details['model_name']

		dict_retrieve_para = {
			                "mode"   : "retrieve",
			                "question" : question,
			                "model" : model_name,
							"k": top_k_context
			            }

		data_with_id = self.predict_mrc_corpus_features(json.dumps(dict_retrieve_para))
		data_mrc_response_list = self.predict_mrc_output(corpus_name, question, top_k_context, data_with_id)

		resp.status = falcon.HTTP_200
		resp.body = json.dumps(data_mrc_response_list)
	# endDef

	def predict_mrc_corpus_features(self, data):
		try:
			res = requests.post(url=self.mrc_corpus_features_url, data=data,
								headers={'Content-Type': 'application/json', 'Connection': 'close'})
			print("inside predict_mrc_corpus after request")
			data_context_id = json.loads(res.text)

			# data_context_id = "65<==>0<==>Prot_000 (3).pdf<==>0<==>0<==>2"
			return data_context_id
		except Exception as error:
			print("Error occurred in predict_mrc_corpus_features", error)
	# endDef

	def predict_mrc_output(self, corpus_name, question, top_k_context, data_with_id):
		try:
			corpusFiles = CorpusFiles()
			corpus_with_files_details = corpusFiles.get_corpus_files_list_by_corpus(corpus_name)

			data_mrc_response_list = []
			if data_with_id['scores'][0] == 0:
				data_with_context = {'mode': "production", 'question': question, 'context': None, "model": "bert_384"}
				data_mrc_response = self.get_predict_response(json.dumps(data_with_context))
				data_mrc_response['file_name'] = None
				data_mrc_response['context'] = None
				data_mrc_response_list.append(data_mrc_response)
			else:
				if len(data_with_id['sections']) < top_k_context:
					top_k_context = len(data_with_id['sections'])

				for context_idx in range(top_k_context):
					data_context = self.get_context_from_id(data_with_id['sections'][context_idx], corpus_with_files_details)
					data_with_context = {'mode': "production", 'question': question,
										 'context': data_context['context_data'],
										 "model": "bert_384"}
					data_mrc_response = self.get_predict_response(json.dumps(data_with_context))
					data_mrc_response['file_name'] = data_context['file_name']
					data_mrc_response['context'] = data_context['context_data']
					data_mrc_response_list.append(data_mrc_response)
			return data_mrc_response_list
		except Exception as error:
			print("Error occurred in predict_mrc_output", error)
	# endDef

	def get_context_from_id(self, para_id, corpus_details):
		try:
			extract_context = para_id.split(self.id_separator)
			corpus_id = extract_context[0]
			files_index = int(extract_context[1])
			file_name = extract_context[2]
			pages_index = int(extract_context[3])
			data_index = int(extract_context[4])
			paragraph_index = int(extract_context[5])

			for single_corpus in corpus_details:
				dict_context_data = {}
				if (single_corpus['corpus_id'] == int(corpus_id)) and (single_corpus['file_name'] == file_name):
					dict_context_data['context_data'] = single_corpus['paragraph_json']['files'][files_index]['pages'][pages_index]['data'][data_index]['paragraphs'][paragraph_index]['context']
					dict_context_data['file_name'] = file_name
					return dict_context_data
				# endIf
			# endFor
		except Exception as error:
			print("Error occurred in get_context_from_id", error)
	# endDef

	def get_predict_response(self, data):
		try:
			res = requests.post(url=self.predict_response_url,data=data, headers={'Content-Type': 'application/json', 'Connection':'close'})
			print("inside get_predict_response after request")

			data_with_predict_response = json.loads(res.text)
			return data_with_predict_response
		except Exception as error:
			print("Error occurred in get_predict_response", error)
	# endDef
# endClass