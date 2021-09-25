import falcon
import requests
import json

class FileViewer(object):
	def __init__(self, file_path):
		self.file_path = file_path
		self.response = {}
	# endDef

	def on_post(self, req, resp):
		try:
			req_body = req.stream.read()
			json_data = json.loads(req_body.decode('utf8'))
			
			corpus_name = json_data.get('corpus_name')
			file_name = json_data.get('file_name')
			# file_name = req.get_param('file_name')
			
			fh = open(self.file_path + file_name, 'rb')
			# print(file_name)


			# return json.dumps(payload)
			self.response['message'] = "The file view link for "+ file_name +" is/are successfully generated!"
			self.response['status'] = falcon.HTTP_200
			self.response['data'] = list(fh.read())
			fh.close()

		except (Exception) as error:
			print("Error occured in FileView post response.", error)
			self.response['message'] = "File View Failed!"
			self.response['status'] = falcon.HTTP_500
		
		resp.status = self.response['status']
		resp.body = json.dumps((self.response))
		return resp
	# endDef
# endClass