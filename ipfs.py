import requests
import json


def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    # YOUR CODE HERE
    array = [ {'key' : i, 'value' : data[i]} for i in data]
    array=json.dumps(array)
    #data=json.dumps(Dictionary)
    response = requests.post('https://ipfs.infura.io:5001/api/v0/add', files=json.loads(array),
                         auth=("2FdXTIiRv8TN32iTleW73bF2fDT", "03cea3e5502b95afa44d342fb3485046"))
    

    #hash = p['Hash']
    hash=[]
    dec = json.JSONDecoder()
    i = 0
    while i < len(response.text):
        res, s = dec.raw_decode(response.text[i:])
        i += s+1
        hash.append(res['Hash'])
    return hash


def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    # YOUR CODE HERE	
    params = (
        ('arg', cid),
    )
    response = requests.post('https://ipfs.infura.io:5001/api/v0/cat', params=params,
                             auth=("2FdXTIiRv8TN32iTleW73bF2fDT", "03cea3e5502b95afa44d342fb3485046"))
    data = json.loads(response)
    assert isinstance(data, dict), f"get_from_ipfs should return a dict"
    return data
