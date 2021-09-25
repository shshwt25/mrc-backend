import cgi, os
import cgitb; cgitb.enable()
import json
import falcon
import requests
import configparser
import shutil
from ..answerGeneration.answerGeneration import AnswerGenerator
from ..questionGenerator.questionGenerator import QuestionGenerator
from ..jsonFileStructure.jsonStructureCreation import JsonStructureCreation
from ..trainingParaIdentification.trainingParaIdentification import TrainingParaIdentification

from db.functions.Corpus import Corpus
from db.functions.CorpusFiles import CorpusFiles
from db.functions.QnA import QnA
from services import *

from concurrent.futures import ThreadPoolExecutor
from time import sleep
import threading
from multiprocessing import Process

config = configparser.ConfigParser()
config.read('./services/Config.ini')
model_base_path = config['ServicesConfig']['paragraph_retrieval_model_path']

class FileManagement(object):
	def __init__(self, ):
		self.response 		= {}
		self.corpus_files 	= CorpusFiles()
		self.corpus			= Corpus()
		self.user_id		= 0
	# Handle Corpus and File Deletion
	def delete(self, corpus_name, file_name=None, user_id=0):
		response = {}
		if(file_name==None):
			print('Calling Delete Corpus - None Block')
			response = self.delete_corpus(corpus_name, user_id=0)
		else:
			print('Calling Delete File Block')
			response = self.delete_file(corpus_name,file_name, user_id=0)
		return response

	#Retrain the Entire Corpus after File Deletion
	def retrain_corpus(self, corpus_name, domain_name, user_id):
		print("Start of the Deamon Process : Paragraph Retrieval Retraining")
		print("corpus_name : ",corpus_name, "domain_name : ",domain_name, "user_id : ",user_id)
		para_retrieval_model = TrainingParaIdentification()
		para_retrieval_model.training_para_identification(corpus_name, domain_name, user_id)
		print("End of the Deamon Process : Paragraph Retrieval Retraining")


	#Delete the File and Retrain the Paragraph Identification Task
	def delete_file(self, corpus_name, file_name, user_id):		
		#get the file path to unlink the file
		target_file = self.corpus_files.get_corpus_file_details(corpus_name, file_name)
		corpus_id 	= target_file['corpus_id']
		corpus_details = self.corpus.get_corpus_details_by_id(corpus_id)
		corpus_domain  = corpus_details['domain_name']
		print('corpus domain:', corpus_domain, ',corpus_id:', corpus_id, ',target_file:', target_file['file_url'])     
		try:
			#Delete the Files
			print("Deleting Files :",target_file['file_url'])
			if(os.path.exists(target_file['file_url'])):
				os.remove(target_file['file_url'])
				print("Deleted Files :",target_file['file_url'])
			else:
				print("Files not found :",target_file['file_url'])

			#Clean Up Table
			self.corpus_files.delete_corpus_file_by_name(corpus_name, file_name)

			#Start Deamon to Retrain the Corpus
			target_files = self.corpus_files.get_corpus_all_file_details(corpus_name)
			print('target_files: ' , target_files)
			if len(target_files) > 0:
				processing_thread = Process(target=self.retrain_corpus, args=(corpus_name,corpus_domain,user_id,))
				processing_thread.daemon = True
				processing_thread.start()

		except Exception as e:
			print("Exception in Deleting File : ", e)
		return {"status": file_name+" has been deleted from the corpus!"}
	
	#Entire Corpus Deletion
	def delete_corpus(self, corpus_name, user_id):
		target_files = self.corpus_files.get_corpus_all_file_details(corpus_name)
		try:
			#Delete the Files
			if len(target_files) > 0:            
				for target_file in target_files:
					os.remove(target_file['file_url'])
					print("Deleted File :",target_file['file_url'])

			#Delete the Paragraph Retrieval Model File
			corpus_details = self.corpus.get_corpus_details_by_name(corpus_name)
			print(corpus_details)
			shutil.rmtree(model_base_path+str(corpus_details['corpus_id']))

			#Delete Table Entries in Corpus - Constraint added in Postgres
			response = self.corpus.delete_corpus_by_name(corpus_name)
			print("Corpus Table Deletion : ",response)

		except Exception as e:
			print("Exception in Deleting File with corpus reference : ", e)
		return {"status": "Corpus - "+corpus_name+" has been deleted!"}


	def on_post(self, req, resp):
		file_name = None
		job_mode  = "Corpus"
		req_body = req.stream.read()
		print('req_body: ', req_body)
		json_data = json.loads(req_body.decode('utf8'))
		print('json', json_data)
		corpus_name = json_data.get('corpus_name')
		if(json_data.get('file_name')):
			file_name = json_data.get('file_name')
			job_mode  = "File"
		print('corpus:', corpus_name, ',file_name:', file_name, ',job mode:', job_mode)     
		user_id = 0
        
		if(json_data.get('user_id')):
			user_id = req.get_param('user_id')
		print('user_id', user_id)
		#Initiating Delete
		try:
			response = self.delete(corpus_name, file_name, user_id)
			print("The "+job_mode+" is deleted!", response)
			self.response['message'] = response
			self.response['status'] = falcon.HTTP_200
		except Exception as e:
			print("Deletion of "+job_mode+" Failed : ",e)
			self.response['message'] = "The "+job_mode+" could not be deleted!"
			self.response['status'] = falcon.HTTP_500
		#Falcon API response
		resp.status = self.response['status']
		resp.body = json.dumps((self.response['message']))
		return resp
	# endDef