import cgi, os
import cgitb; cgitb.enable()
import json
import falcon
import requests
import configparser
from .scienceParse import ScienceParse
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
parser_url = config['ServicesConfig']['science_parser_url']
parser_header = {'Content-Type': 'application/pdf'}

class Resource(object):
	def __init__(self, storage_path):
		self._storage_path 	= storage_path
		self.uploaded_files = []
		self.corpus_name	= ''
		self.user_id = 14
		self.uploaded_paths	= {}
		self.path_list		= []
		self.threads		= []
		self.thread_count	= 4
		self.response 		= {}


	# def qna_generator(self, dict_file_details, corpus_name, fileitem, fn):
	def qna_generator(self, corpus_name, domain_name):
		print("********************************************")
		print("********************************************")
		print("********************************************")
		print("********************************************")
		print("********************************************")
		print("Inside the Deamon Process")
		#Iterate over files
		for each_uploaded_file in self.path_list:
			print("********************************************")
			print("Processing File : " + each_uploaded_file['file_name'])
			print("********************************************")
			# update status in progress in qna
			# ans_gen_in_progress
			qna_insert_in_progress = QnA()
			qna_insert_in_progress.insert_qna(corpus_name, each_uploaded_file['file_name'], None, None, 'Y', 'ans_gen_in_progress')

			science_parser = ScienceParse()
			list_parser_response = science_parser.get_parsed_data(each_uploaded_file, parser_url, parser_header)
			
			#Creation of JSON Structure
			jsc = JsonStructureCreation()
			final_struct = jsc.JsonFileStructure("v2.0", self.corpus_name, list_parser_response)
			paragraph_json = json.dumps(final_struct)

			#Adding of the current file to the corpus files table
			corpus_files = CorpusFiles()
			# corpus_name, file_name, file_url, file_type, paragraph_json, active='Y'
			corpus_files.update_corpus_file(self.corpus_name, each_uploaded_file['file_name'], self._storage_path + each_uploaded_file['file_name'], each_uploaded_file['file_name'].split(".")[-1],paragraph_json)

			#Generating answers from the Quans library
			ans = AnswerGenerator()
			para_json_with_ans = ans.get_answer_data(self.corpus_name, each_uploaded_file, paragraph_json)
			print("********************************************")
		# endFor
		tpi = TrainingParaIdentification()
		tpi.training_para_identification(corpus_name, domain_name, self.user_id)


		print("End of the Deamon Process")
		print("********************************************")
		print("********************************************")
		print("********************************************")
		print("********************************************")
		print("********************************************")
		# #Send the complete list of files to Science Parser
		# science_parser = ScienceParse()
		# list_parser_response = science_parser.get_parsed_data(dict_file_details, parser_url, parser_header)

		# # print(list_parser_response_added)
		# jsc = JsonStructureCreation()
		# final_struct = jsc.JsonFileStructure("v2.0", corpus_name, list_parser_response)

		# # print(final_struct)
		# paragraph_json = json.dumps(final_struct)
		# corpus_files = CorpusFiles()

		# corpus_files.update_corpus_file(corpus_name, fileitem.filename, self._storage_path + fn, fn.split(".")[-1],paragraph_json)
		
		# ans = AnswerGenerator()
		# para_json_with_ans = ans.get_answer_data(corpus_name, fileitem, paragraph_json)


	def generate_list_of_paths(self, upload_paths):
		self.path_list = []
		for each_path in upload_paths:
			self.path_list.append(upload_paths[each_path])
			corpus_files = CorpusFiles()
			current_file = upload_paths[each_path]['file_name']
			corpus_files.insert_corpus_file(self.corpus_name, current_file, self._storage_path + current_file, current_file.split(".")[-1],None)

	def upload_files(self,input_file_list):
		self.uploaded_files = []
		self.uploaded_paths	= {}
		self.path_list		= []
		for i in range(len(input_file_list)):
			fileitem = input_file_list[i]
			if fileitem.filename:
				fn = os.path.basename(fileitem.filename)
				print("I ===",i)
				print(fileitem.filename)
				dict_file_details = {"file_name" : fileitem.filename, "pdf_filespath" : self._storage_path + fn,      			      "total_pages": 1}
				self.uploaded_paths[fileitem.filename]=dict_file_details
				self.uploaded_files.append(fn)
				open(self._storage_path + fn, 'wb').write(fileitem.file.read())
				self.response['message'] = 'The file "' + fn + '" was uploaded successfully'
			else:
				self.response['message'] = 'No file was uploaded'

	def on_post(self, req, resp):
		domain_name = req.get_param('domain_name')
		corpus_name = req.get_param('corpus_name')
		self.corpus_name = corpus_name
		self.domain_name = domain_name
		user_id = req.get_param('user_id')
		input_file_list = req.get_param_as_list('file')
		print("input file list",len(input_file_list))

		try:
			#Check Required Fields
			if(len(input_file_list)>0 and (domain_name=='' or domain_name!=' ') and (corpus_name!='' or corpus_name!=' ')):
				#CORPUS to Database
				#Check for existing corpus detail in database
				corpus = Corpus()
				corpus_exists = corpus.get_corpus_id(domain_name, corpus_name)
				print(corpus_exists)
				if corpus_exists:
					print('corpus exists')
				else:
					print('corpus does not exist')
					#Adding of Corpus if it doesnot exist
					corpus.insert_corpus(domain_name, corpus_name, self.user_id)

				#Uploading files in thread - Bare Minimum for API to send response
				#for i in range(1,len(input_file_list)):
				#	thread = threading.Thread(target=self.upload_files, args=(input_file_list,))
				#	self.threads.append(thread)
				#	print("Threads : ",len(self.threads))
				#	thread.start()
				# message = self.upload_files(input_file_list)
				#for thread in self.threads:
				#	thread.join()
				msg = self.upload_files(input_file_list)
				self.uploaded_files = list(set(self.uploaded_files))
				print("List of Uploaded Files",(self.uploaded_files))
				print("List of Uploaded Paths",(self.uploaded_paths))
				#Converted list of paths
				self.generate_list_of_paths(self.uploaded_paths)
				print("List of Uploaded Paths",self.path_list)


				#Deamon Thread for Question
				# self.qna_generator(self, dict_file_details, corpus_name, fileitem, fn)
				processing_thread = Process(target=self.qna_generator, args=(self.corpus_name,domain_name,))
				processing_thread.daemon = True
				processing_thread.start()

				self.response['message'] = "The file(s) "+str(self.uploaded_files)+" is/are successfully uploaded!"
				self.response['status'] = falcon.HTTP_200
			else:
				self.response['message'] = "The required fields are missing! Please check your requests!"
				self.response['status'] = falcon.HTTP_400
		except Exception as e:
			# raise falcon.HTTPBadRequest(
			#         'File Upload Failed',
			#         '{}'.format(e))
			print(e)
			self.response['message'] = "File Upload Failed!"
			self.response['status'] = falcon.HTTP_500
			
		#Falcon API response
		resp.status = self.response['status']
		resp.body = json.dumps((self.response['message']))
		return resp
	# endDef