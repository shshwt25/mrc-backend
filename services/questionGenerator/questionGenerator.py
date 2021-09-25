import falcon
import requests
import json
import re
import configparser
from db.functions.QnA import QnA

import threading

class QuestionGenerator():
	def __init__(self):
		config = configparser.ConfigParser()
		config.read('./services/Config.ini')
		self.question_generation_url = config['ServicesConfig']['question_generation_url']

	def on_post(self, req, resp):
		try:
			qna_json = json.load(req.bounded_stream,encoding='utf-8')
			dataset_json = qna_json['file_updated_answers']

			corpus_name = dataset_json['corpus_name']
			file_name = dataset_json['files'][0]['file_name']
			
			qna_update_db = QnA()
			if(qna_json['user_updated'].lower() == "no"):
				print("Inside no in block")
				qna_update_db.update_qna(corpus_name, file_name, None, None, "ques_gen_in_progress")
				
				deamon_thread = threading.Thread(target=self.deamon_question_data, name='Thread_question_data', args=(dataset_json, corpus_name, file_name))
				deamon_thread.daemon = True 
				deamon_thread.start()

				resp.status = falcon.HTTP_200
				resp.body = json.dumps({"success" : "Question Generator is running in background."})
			# endIf
			
			if(qna_json['user_updated'].lower() == "yes"):
				print("Inside yes in block")
				qna_update_db.update_qna(corpus_name, file_name, None, dataset_json, None)
				resp.status = falcon.HTTP_200
				resp.body = json.dumps({"success" : "Json data updated in database."})
			# endIf
			
			return resp
		except Exception as e:
			print(e)
			resp.status = falcon.HTTP_500
			resp.body = json.dumps({"error_msg": "Question Generation Failed!"})
	# defDef

	def deamon_question_data(self, dataset_json, corpus_name, file_name):
		print("Inside deamon_question_data method.")

		qna_deamon_db = QnA()
		ques_gen_res = self.get_question_data(dataset_json)

		qna_deamon_db.update_qna(corpus_name, file_name, ques_gen_res, None, "ques_gen_completed")
		
		print("Updated question_data in deamon thread.")
	# endDef
	
	def get_question_data(self, data_with_ans):
		print("inside get_question_data method")
		data_for_qna = json.dumps(data_with_ans)
		ques_gen_res = requests.post(url=self.question_generation_url,data=data_for_qna, headers={'Content-Type': 'application/json', 'Connection':'close'})
		return(json.loads(ques_gen_res.text))
