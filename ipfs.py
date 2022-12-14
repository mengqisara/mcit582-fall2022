import requests
import json
def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
	files = {'file': json.dumps(data)}
	response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=files, auth=('2FdXTIiRv8TN32iTleW73bF2fDT','03cea3e5502b95afa44d342fb3485046'))
	cid = response.json()['Hash']
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	https://ipfs.infura.io:5001/api/v0/cat?arg={content ID}
	# print(cid)
	params = (('arg',cid),)
	response = requests.post('https://ipfs.infura.io:5001/api/v0/cat', params=params, auth=('2FdXTIiRv8TN32iTleW73bF2fDT','03cea3e5502b95afa44d342fb3485046'))
	data = json.loads(response.text)
	# print(data)
	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
