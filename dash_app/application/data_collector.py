import requests
import json

class DataCollector:

	recent_request = None

	def __init__(self):
		return None

	def get(self, url, params):
		response = requests.get(url=url, 
			params=params)

		return response

	def save_to_json_file(self, response, to_file):
		with open(to_file, "wb") as f:
			for chunk in response.iter_content(chunk_size=128):
				f.write(chunk)
			f.close()

       




