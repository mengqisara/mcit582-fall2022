import hashlib


class Block:
	def __init__(self, index, timestamp, content, previous_hash):
		self.index = index
		self.timestamp = timestamp
		self.content = content
		self.previous_hash = previous_hash
		self.hash = self.calc_hash()

	def calc_hash(self):
		sha = hashlib.sha256()
		sha.update(str(self.index).encode('utf-8') +
				   str(self.timestamp).encode('utf-8') +
				   str(self.content).encode('utf-8') +
				   str(self.previous_hash).encode('utf-8'))
		return sha.hexdigest()


M4BlockChain = []

from datetime import datetime


def create_genesis_block():
	return Block(0, datetime.now(), "Genesis Block", "0")


M4BlockChain.append(create_genesis_block())


# write a function `next_block` to generate a block
def next_block(last_block):
	return Block(last_block.index+1,datetime.now(),"this is block "+last_block.index+1,str(last_block.calc_hash()))



# append 5 blocks to the blockchain
def app_five(block_list):
	k=5
	while k>0:
		block_list.append(next_block(block_list[-1]))
		k-=1
	return
