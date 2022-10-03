import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	files = {
	'file': data
	}

	response = requests.post(
	'https://ipfs.infura.io:5001/api/v0/add',
	files=files,
	auth=(
	'id',
	'secret')
	)

	return response.text.split(",")[1].split(":")[1].replace('"','')

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
	params = (
	('arg',cid),
	)
	response = requests.post('https://ipfs.infura.io:5001/api/v0/cat', params=params, auth=('id',
	'secret'))

	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return response.json()
