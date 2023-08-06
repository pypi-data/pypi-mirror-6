import requests
import json

api = 'http://localhost:5000'

def getMessage():
	r = requests.get(api + '/message')
	try:
		r.raise_for_status()
		result = r.json()
		return result['message']
	except Exception:
		raise


def postMessage(msg):
	data = {'message': msg}
	headers = {'content-type': 'application/json'}

	r = requests.post(api + '/new', data=json.dumps(data), headers=headers)
	try:
		r.raise_for_status()
		print("Message submitted sucessfully")
	except Exception:
		raise