import json
import requests

class ScienceParse():
	def get_parsed_data(self, dict_file_details,parser_url,parser_header):
		list_parser_response_added = []
		data = open(dict_file_details["pdf_filespath"], 'rb').read()
		res = requests.post(url=parser_url,data=data, headers=parser_header)
		dict_parser_response = json.loads(res.text)
		dict_file_details["parser_response"] = dict_parser_response
		list_parser_response_added.append(dict_file_details)
		# endFor
		return(list_parser_response_added)
			
	# endDef
# endClass