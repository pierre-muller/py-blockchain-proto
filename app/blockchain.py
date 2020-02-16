
from flask_restplus import Resource, marshal_with, marshal

import hashlib
from flask import request

import json

from app.restplus import api
from app.serializers import blockchain, balances, block
from app.parsers import transaction_arguments
from app.client import Client

import logging

ns_blockchain = api.namespace('blockchain', description='Operations related to the blockchain')



class Transaction(object):
	fromAccount = ""
	toAccount = ""
	amount = 0.0
	def __init__(self, fromAccount, toAccount, amount):
		self.fromAccount = fromAccount
		self.toAccount = toAccount
		self.amount = amount

	def __repr__(self):
		return json.dumps(self.__dict__)


class Block(object):
	prevHash = ""
	ownHash = ""
	nounce = 0
	index = 0
	def __init__(self, index, prevHash):
		self.prevHash = prevHash
		self.index = index
		self.transactions = []
		self.nounce = 0

	def addTransaction(self, fromAccount, toAccount, amount):
		self.transactions.append(Transaction(fromAccount, toAccount, amount))


	
	def mine(self):
		print("mining block: " + self.toJson())
		#print(hashlib.md5(self.toJson().encode()).hexdigest())
		
		while not(hashlib.md5(self.toJson().encode()).hexdigest().startswith("00")) :
			#print("{} {}".format(self.nounce, hashlib.md5(self.toJson().encode()).hexdigest()))
			self.nounce += 1
		self.ownHash = hashlib.md5(self.toJson().encode()).hexdigest()
		logging.info("found nounce: {} giving hash value: {}".format(self.nounce, self.ownHash))
		

	def toJson(self):
		buf=json.dumps([ob.__dict__ for ob in self.transactions])
		buf='{"prevHash":"' + self.prevHash + '", "nounce":"' + str(self.nounce) + '","index":"' + str(self.index) + '", "transactions":' + buf + '}'
		return buf
	
	def computeHash(self):
		return  hashlib.md5(self.toJson().encode()).hexdigest()





class Account(object):
	name=""
	balance=0.0

	def __init__(self, name, balance):
		self.name = name
		self.balance = balance

class Accounts(object):
	def __init__(self):
		self.accounts=[]



class Blockchain(object):
	def __init__(self):
		self.blocks=[]
		block = Block(0, "genesis")
		block.addTransaction("alice","alice",1000)
		block.mine()
		self.blocks.append(block)

	def createNewBlock(self):
	
		prevBlock = self.blocks[-1]
		block = Block(prevBlock.index + 1, prevBlock.ownHash)
		return block

	def getBalances(self):
		balances = {}
		for block in self.blocks:
			for transaction in block.transactions:
				if block.index == 0:
					if transaction.toAccount not in balances:
						balances[transaction.toAccount] = 0.0
					balances[transaction.toAccount] += transaction.amount
				else :
					if transaction.toAccount not in balances:
						balances[transaction.toAccount] = 0.0
					if transaction.fromAccount not in balances:
						balances[transaction.fromAccount] = 0.0
					balances[transaction.fromAccount] -= transaction.amount
					balances[transaction.toAccount] += transaction.amount
		return balances

	""" in this implementation, only one block at a time is added to the blockchain
	to validate the chain, we can therefore consider the chain minus its last block to be
	valid.
	hence, the following checks are sufficient:
	 - balances are >=0
	 - chaining conditions of last block are valid (index and prevhash)
	 - hash of last block
	"""
	def isValid(self):
		#check balances
		balances = self.getBalances()
		for b in balances:
			if balances[b] < 0:
				logging.debug("blockchain isValid(): invalid balance for {}".format(balances[b]))
				return False

		if not self.blocks:
			logging.debug("blockchain isValid(): empty chain is valid")
			return True

		if len(self.blocks) == 1:
			if (self.blocks[0].prevHash == 'genesis'
				and self.blocks[0].computeHash() == self.blocks[0].ownHash):
				return True
			else:
				logging.debug("blockchain isValid(): invalid genesis block")
				return False


		if (self.blocks[-2].ownHash != self.blocks[-1].prevHash
				or self.blocks[-2].index != self.blocks[-1].index -1 ):
			logging.debug("blockchain isValid(): invalid chain linkage on last block")
			return False

		if (self.blocks[-1].computeHash() != self.blocks[-1].ownHash):
			logging.debug("blockchain isValid(): invalid hash on last block")
			return False

		return True



@ns_blockchain.route('/')
class BlockchainEndpoint(Resource):


	@api.marshal_with(blockchain)
	def get(self):
		return Client.instance.blockchain, 200

@ns_blockchain.route('/balances')
class balances(Resource):

	@api.marshal_with(balances)
	def get(self):
		bal = Client.instance.blockchain.getBalances()
		acc = Accounts()
		for name in bal:
			acc.accounts.append(Account(name, bal[name]))
		return acc, 200


@ns_blockchain.route('/sendTransaction/')
class sendTransaction(Resource):

	@api.expect(transaction_arguments)
	def post(self):

		args = transaction_arguments.parse_args()
		balances = Client.instance.blockchain.getBalances()
		if (args['fromAccount'] not in balances or balances[args['fromAccount']] < args['amount']) and Client.instance.honest:
			return "Insufficient funds", 403

		newBlock = Client.instance.blockchain.createNewBlock()
		newBlock.addTransaction(args['fromAccount'], args['toAccount'], args['amount'])
		newBlock.mine()
		Client.instance.blockchain.blocks.append(newBlock)
		if not Client.instance.blockchain.isValid() and Client.instance.honest:
			Client.instance.blockchain.blocks.pop()
			return "Insufficient funds", 403

		# forward new block to peers
		Client.instance.propagateBlockToPeers(newBlock)


		return "Done", 201


@ns_blockchain.route('/acceptBlock/')
class acceptBlock(Resource):
	@api.expect(block)
	def post(self):
		try:
			newBlock = Block(request.json['index'], request.json['prevHash'])
			newBlock.ownHash = request.json['ownHash']
			newBlock.nounce = request.json['nounce']
			if 'transactions' in request.json:
				for transaction in request.json['transactions']:
					newBlock.addTransaction(transaction['fromAccount'], transaction['toAccount'], transaction['amount'])

			Client.instance.blockchain.blocks.append(newBlock)

			logging.debug("Try accepting block")
			logging.debug(Client.instance.blockchain.getBalances())
			if Client.instance.blockchain.isValid():
				return "Accepted", 201

			else:
				Client.instance.blockchain.blocks.pop()
				Client.instance.rejectedBlocks.append(newBlock)
				return "Rejected", 403
		except e:
			logging.exception("Unexpected error")
			return "Unexpected error", 500