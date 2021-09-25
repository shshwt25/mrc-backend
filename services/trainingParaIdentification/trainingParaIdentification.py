import falcon
import requests
import json
import configparser

from db.functions.CorpusFiles import CorpusFiles
from db.functions.Corpus import Corpus

class TrainingParaIdentification():
	def __init__(self):
		# self.corpus_name = ''
		# self.question = ''
		config = configparser.ConfigParser()
		config.read('./services/Config.ini')
		self.get_context_url = config['ServicesConfig']['get_context_url']
		
		# self.predict_response_url = config['ServicesConfig']['predict_response_url']
		self.id_separator = '<==>'
		self.mrc_corpus_features_url = config['ServicesConfig']['mrc_corpus_features_url']
	# endDef

	def train_mrc_corpus(self, data):
		try:
			res = requests.post(url=self.mrc_corpus_features_url,data=data, headers={'Content-Type': 'application/json', 'Connection':'close'})
			print("inside train_mrc_corpus after request")
			data_index_filename = json.loads(res.text)
			
			# data_index_filename = {"status" : "trained", "corpus_id": 14, "model_path": "sample_tfidf.npz"}
			return(data_index_filename['model_path'])
		except (Exception) as error:
			print("Error occured in train_mrc_corpus", error)
	# endDef

	def generate_paralist_all_files(self, corpus_details):
		try:
			list_paragraph_item = []

			for single_corpus in corpus_details:
				para_json = single_corpus["paragraph_json"]
				corpus_id = single_corpus["corpus_id"]
				files_index = 0
				for file_item in para_json["files"]:
					file_name = file_item["file_name"]
					pages_index = 0
					for page_item in file_item["pages"]:
						data_index = 0
						for data_item in page_item["data"]:
							paragraph_index = 0
							for para_item in data_item["paragraphs"]:
								dict_paragraph_item = {}
								para_id = str(corpus_id) + self.id_separator + str(files_index) + self.id_separator + file_name + self.id_separator + str(pages_index) + self.id_separator + str(data_index) + self.id_separator + str(paragraph_index)
								dict_paragraph_item["id"] = para_id
								dict_paragraph_item["text"] = para_item["context"]
								list_paragraph_item.append(dict_paragraph_item)
								paragraph_index += 1
							# endFor
							data_index += 1
						# endFor
						pages_index += 1
					# endFor
					files_index += 1
				# endFor
			# endFor
			return(list_paragraph_item)
		except (Exception) as error:
			print("Error occured in generate_paralist_all_files", error)
	# endDef

	def training_para_identification(self, corpus_name, domain_name, user_id):
		try:
			corpusFiles = CorpusFiles()
			corpus_details = corpusFiles.get_corpus_files_list_by_corpus(corpus_name)
			
			list_paragraph_item = []
			list_paragraph_item = self.generate_paralist_all_files(corpus_details)
			dict_train_mrc = {
							    "corpus_id": str(corpus_details[0]['corpus_id']),
							    "mode": "train",
							    "model_name": corpus_name + "_model",
							    "payload": list_paragraph_item
							}
			
			model_path = self.train_mrc_corpus(json.dumps(dict_train_mrc))

			corpus = Corpus()
			update_msg = corpus.update_model_name(corpus_name, domain_name, user_id, model_path)
			
			return(list_paragraph_item)
		except (Exception) as error:
			print("Error occured in training_para_identification", error)
	# endDef
# endClass

# if __name__ == '__main__':
# 	tpi = TrainingParaIdentification()
# 	tpi.training_para_identification("clinical", "domain clinical", 14)