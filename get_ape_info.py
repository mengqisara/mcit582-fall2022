from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
api_url = f"https://mainnet.infura.io/v3/255d23fd3a1c45cda194d2f09486a53f"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(apeID):
	assert isinstance(apeID,int), f"{apeID} is not an int"
	assert 1 <= apeID, f"{apeID} must be at least 1"

	data = {'owner': "", 'image': "", 'eyes': "" }
	
	#YOUR CODE HERE	
	contract = web3.eth.contract(address=contract_address,abi=abi)
	result = contract.functions.tokenURI(apeID).call()
	result = result.replace("ipfs://","")
	owner = contract.address
	
	

	ABI_ENDPOINT = 'https://ipfs.infura.io:5001/api/v0/cat'
	params = {
		'arg': result
	}
	try:
		response = requests.post( 'https://ipfs.infura.io:5001/api/v0/cat', params=params, auth=('2FdXTIiRv8TN32iTleW73bF2fDT','03cea3e5502b95afa44d342fb3485046'))
		res1 = json.loads(json.dumps(response.json()))
	except Exception as e:
		print( f"Failed to get {result} from IPFS node" )
		print( e )
	
	data['owner']='nice'
	data['image']=res1['image']
	data['eyes']=res1['attributes'][4]['value']

	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

