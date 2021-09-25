import falcon
import requests
import json

from db.functions.User import User

class Login(object):
	def __init__(self):
		self.response = {}
	# endDef

	def on_post(self, req, resp):
		try:
			req_body = req.stream.read()
			json_data = json.loads(req_body.decode('utf8'))
			
			user_name = json_data.get('username')
			password = json_data.get('password')

			user = User()
			user_details = user.get_user_by_user_name(user_name)

			allow_user = False

			if(user_details is None):
				message = "No user found with this id."
				allow_user = False
			elif(len(user_details) > 1):
				message = "Multiple user found in db with this id."
				allow_user = False
			elif(len(user_details) == 1):
				# print(user_details)
				if(user_details[0]['password'] == password):
					message = "User found."
					allow_user = True
				else:
					message = "Password Incorrect"
					allow_user = False
				# endIf
			# endIf

			if(allow_user == True):
				user_id = user_details[0]['id']
			else:
				user_id = None

			# user_details = user.test()

			# print(user_details)
			
			self.response['message'] = message
			self.response['allow_user'] = allow_user
			self.response['user_id'] = user_id
			self.response['groups'] = user_details[0]['groups']
			self.response['status'] = falcon.HTTP_200

		except (Exception) as error:
			print("Error occured in Login post response.", error)
			self.response['message'] = "User not found!"
			self.response['allow_user'] = False
			self.response['user_id'] = -1
			self.response['status'] = falcon.HTTP_500
		
		resp.status = self.response['status']
		resp.body = json.dumps((self.response))
		return resp
	# endDef
# endClass