from vyper.interfaces import ERC20

tokenAQty: public(uint256) #Quantity of tokenA held by the contract
tokenBQty: public(uint256) #Quantity of tokenB held by the contract

invariant: public(uint256) #The Constant-Function invariant (tokenAQty*tokenBQty = invariant throughout the life of the contract)
tokenA: ERC20 #The ERC20 contract for tokenA
tokenB: ERC20 #The ERC20 contract for tokenB
owner: public(address) #The liquidity provider (the address that has the right to withdraw funds and close the contract)

@external
def get_token_address(token: uint256) -> address:
	if token == 0:
		return self.tokenA.address
	if token == 1:
		return self.tokenB.address
	return empty(address)

# Sets the on chain market maker with its owner, and initial token quantities
@external
def provideLiquidity(tokenA_addr: address, tokenB_addr: address, tokenA_quantity: uint256, tokenB_quantity: uint256):
	assert self.invariant == 0 #This ensures that liquidity can only be provided once
	#Your code here
	self.tokenA.address=tokenA_addr
	self.tokenB.address=tokenB_addr
	self.tokenAQty = tokenA_quantity
	self.tokenBQty = tokenB_quantity
	send(self.tokenA.address,tokenA_quantity)
	send(self.tokenB.address,tokenB_quantity)
	assert self.invariant > 0

@internal
def _tradeTokenAtoB(sell_quantity: uint256):
	self.tokenA.transferFrom(msg.sender,self.tokenA.address,sell_quantity)
	new_total_tokenA: uint256 = self.tokenAQty+sell_quantity
	new_total_tokenB: uint256 = self.invariant/new_total_tokenA
	tokenB_to_send: uint256 = self.tokenBQty-new_total_tokenB
	self.tokenB.transfer(msg.sender,tokenB_to_send)
	self.tokenAQty=new_total_tokenA
	self.tokenBQty=new_total_tokenB

@internal
def _tradeTokenBtoA(sell_quantity: uint256):
	self.tokenB.transferFrom(msg.sender,self.tokenB.address,sell_quantity)
	new_total_tokenB: uint256 = self.tokenBQty+sell_quantity
	new_total_tokenA: uint256 = self.invariant/new_total_tokenB
	tokenA_to_send: uint256 = self.tokenAQty-new_total_tokenA
	self.tokenA.transfer(msg.sender,tokenA_to_send)
	self.tokenAQty=new_total_tokenA
	self.tokenBQty=new_total_tokenB
# Trades one token for the other
@external
def tradeTokens(sell_token: address, sell_quantity: uint256):
	assert sell_token == self.tokenA.address or sell_token == self.tokenB.address
	#Your code here
	if(sell_token==self.tokenA.address):
		self._tradeTokenAtoB(sell_quantity)
	else:
		self._tradeTokenBtoA(sell_quantity)

# Owner can withdraw their funds and destroy the market maker
@external
def ownerWithdraw():
	assert self.owner == msg.sender
	self.tokenA.transfer(self.owner,self.tokenAQty)
	self.tokenB.transfer(self.owner,self.tokenBQty)



