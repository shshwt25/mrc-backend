import falcon
import requests
import json
import csv
from db.functions.QnA import QnA
import os

class QnADownloader(object):
	def __init__(self, qna_csv_path):
		self.csv_path = qna_csv_path
		self.response = {}
	# endDef

	def on_post(self, req, resp):
		try:
			req_body = req.stream.read()
			json_data = json.loads(req_body.decode('utf8'))
			
			corpus_name = json_data.get('corpus_name')
			file_name = json_data.get('file_name')
			
			qna = QnA()
			status, qna = qna.get_qna(corpus_name, file_name)
			# print(qna)
			
			qna_file_name = self.dump_to_csv(qna['files'][0])
			fh = open(self.csv_path + qna_file_name, 'rb')
			
			self.response['message'] = "The file download link for "+ file_name +" is/are successfully generated!"
			self.response['status'] = falcon.HTTP_200
			self.response['data'] = list(fh.read())
			self.response['qna_file_name'] = qna_file_name
			fh.close()

		except (Exception) as error:
			print("Error occured in FileView post response.", error)
			self.response['message'] = "File View Failed!"
			self.response['status'] = falcon.HTTP_500
		
		os.remove(self.csv_path + qna_file_name)
		resp.status = self.response['status']
		resp.body = json.dumps((self.response))
		return resp
	# endDef
	
	def dump_to_csv(self, file_data):
		csv_data = {}

		# with open(self.csv_path + 'qna.csv', mode='w') as writeFile:
		# 	writer = csv.writer(writeFile)
			
		file_name = 'QNA_' + file_data['file_name'].split('.')[0] + '.csv'
		with open(self.csv_path + file_name, mode='w', newline='\n', encoding='utf-8') as csv_file:
			fieldnames = ['title', 'question', 'answer']
			writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
			writer.writeheader()
			
			for file in file_data['pages']:
				for data_item in file['data']:
					for para in data_item['paragraphs']:
						if('qas' in para):
							for qas_data in para['qas']:
								dict_csv_data = {}
								dict_csv_data['title'] = para['title']	
								dict_csv_data['question'] = qas_data['question']
								dict_csv_data['answer'] = qas_data['answers'][0]['text']
								writer.writerow(dict_csv_data)

								# list_csv_data = []
								# list_csv_data.append(para['title'])
								# list_csv_data.append(qas_data['question'])
								# list_csv_data.append(qas_data['answers'][0]['text'])
								# writer.writerow(list_csv_data)
							# endFor
						# endIf
					# endFor
				# endFor
			# endFor
			csv_file.close()
		# endFileWriter
		return file_name
	# endDef

# endClass