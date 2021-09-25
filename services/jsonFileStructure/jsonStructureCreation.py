import json
import re

class JsonStructureCreation():
	# def __init__(self, version, corpus_name, list_parser_response_added):
	# 	self.version = version
	# 	self.corpus_name = corpus_name
	# 	self.list_parser_response_added = list_parser_response_added
	# files = open("sample_out.txt", "r")

	def ReadInputJson(filepath):
		with open(filepath, encoding="utf8") as f:
			lines = f.readlines()
		dict_pdf = json.loads(lines[0])
		return dict_pdf["metadata"]["sections"]
	# endDef

	def FilterTextfileData(self, dict_parser_response):
		list_sections = dict_parser_response["sections"]
		
		list_splited_lines = []
		rx = re.compile(r'(.)\1{9,}')
		for item in list_sections:
			try:
				dict_splited_lines = {}
				if(item["heading"] == None or item["text"].strip() == ""):
					pass
				elif(rx.search(item["text"])):
					pass
				else:
					removed_newline_title = item["heading"].strip().replace('\n', ' ')
					removed_newline_context = item["text"].strip().replace('\n', ' ')

					dict_splited_lines["title"] = removed_newline_title
					dict_splited_lines["context"] = removed_newline_context
					list_splited_lines.append(dict_splited_lines)
			except KeyError as e:
				err = {'error': e}
		return list_splited_lines


	def JsonFileStructure(self, version, corpus_name, list_parser_response_added):
		# list_splited_lines = FilterTextfileData(input_json_filepath)
		# 'file_name': 'sample1.pdf', 'pdf_filespath': './documents/sample1.pdf', 'total_pages': 1, 'parser_response': 
		data = {
			"version": version,
			"corpus_name": corpus_name
		}
		list_files = []
		for fn in list_parser_response_added:
			
			list_pages = []
			i = 0
			while i < int(fn["total_pages"]):
				
				list_data = [] # add loop if data has more items
				list_para = []
				for ln in self.FilterTextfileData(fn["parser_response"]):
					dict_para_items = {}
					dict_para_items["title"] = ln["title"]
					dict_para_items["context"] = ln["context"]
					list_para.append(dict_para_items)
				# endFor

				dict_data_items = {}
				dict_data_items["paragraphs"] = list_para # paragraph list ready
				
				list_data.append(dict_data_items) # data list ready
				
				dict_pages_item = {}
				dict_pages_item["page_num"] = i
				dict_pages_item["data"] = list_data

				list_pages.append(dict_pages_item)
				i += 1
			# endWhile 
			
			dict_file_item = {}
			dict_file_item["file_name"] = fn["file_name"]
			dict_file_item["pages"] = list_pages

			list_files.append(dict_file_item)
		# endFor

		data["files"] = list_files
		# print(data)

		# Serialize the list of dicts to JSON
		# j = json.dumps(data, indent=2)
		# json_file_name = "C:\\Python\\ICCA\\ICCA_API\\output_000.json"
		# # Write to file
		# with open(json_file_name, 'w') as f:
		# 	f.write(j)
		# 	print("Creating JSON file.")
		return data
	# endDef


