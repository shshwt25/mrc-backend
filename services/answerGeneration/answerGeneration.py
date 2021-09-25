import json
import requests
import configparser
from db.functions.QnA import QnA

class AnswerGenerator():
	def __init__(self):
		print("inside answer generation")
		config = configparser.ConfigParser()
		config.read('./services/Config.ini')
		self.answer_generation_url = config['ServicesConfig']['answer_generation_url']
		self.question_generation_url = config['ServicesConfig']['question_generation_url']
	# endDef

	def get_answer_data(self, corpus_name, fileitem, data):
		res = requests.post(url=self.answer_generation_url,data=data, headers={'Content-Type': 'application/json', 'Connection':'close'})
		print("inside get_answer_data after request")
		
		data_with_ans = json.loads(res.text)
		
		qna = QnA()
		
		# change to update
		# update status completed in qna
		# ans_gen_completed
		qna.update_qna(corpus_name, fileitem['file_name'], data_with_ans, None, 'ans_gen_completed')
		return(data_with_ans)
	# endDef
# endClass