
from flask_restplus import Resource, marshal_with, marshal

import hashlib
from flask import request

import json

from app.restplus import api
from app.serializers import blockchain, balances, block
from app.parsers import transaction_arguments
from app.node import Node

import logging


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


	
	def isValid(self, prevBalances={}, fullCheck = True):
		if not self.blocks:
			logging.debug("blockchain isValid(): empty chain is valid")
			return True, {}

		"""
		if not prevBalances:
			lastNode = self.blocks.pop()
			prevBalances = self.getBalances()
			self.blocks.append(lastNode)
		"""

		if len(self.blocks) == 1:
			if (self.blocks[0].prevHash == 'genesis'
				and self.blocks[0].computeHash() == self.blocks[0].ownHash):
				balances = {}
				for transaction in self.blocks[0].transactions:
					if transaction.toAccount not in balances:
						balances[transaction.toAccount] = 0.0
					balances[transaction.toAccount] += transaction.amount
				return True, balances
			else:
				logging.debug("blockchain isValid(): invalid genesis block")
				return False, {}

		lastBlock = self.blocks.pop()
		if fullCheck :
			prevValid, prevBalances = self.isValid()
		else:
			prevValid = True
		self.blocks.append(lastBlock)
		


		if not prevValid:
			logging.debug("blockchain isValid(): invalid block at index: {}".format(lastBlock.index-1))
			return False, {}


		#check balances
		balances = prevBalances
		for transaction in self.blocks[-1].transactions:
			if transaction.toAccount not in balances:
				balances[transaction.toAccount] = 0.0
			if transaction.fromAccount not in balances:
				balances[transaction.fromAccount] = 0.0
			balances[transaction.fromAccount] -= transaction.amount
			balances[transaction.toAccount] += transaction.amount

		for b in balances:
			if balances[b] < 0:
				logging.debug("blockchain isValid(): invalid balance for {} in block at index {}.".format(b, lastBlock.index))
				return False, {}


		if (self.blocks[-2].ownHash != self.blocks[-1].prevHash
				or self.blocks[-2].index != self.blocks[-1].index -1 ):
			logging.debug("blockchain isValid(): invalid chain linkage on last block")
			return False, {}

		if (self.blocks[-1].computeHash() != self.blocks[-1].ownHash):
			logging.debug("blockchain isValid(): invalid hash on last block")
			return False, {}

		return True, balances



	def isFullChainValid(self):
		return self.isValid()[0]


	"""
	when adding one block to the chain, no need to check the full chain is valid
	as we know it was valid before the addition
	"""
	def isLastBlockValid(self):
		lastBlock = self.blocks.pop()
		prevBalances = self.getBalances()
		self.blocks.append(lastBlock)
		
		return self.isValid(prevBalances, False)[0]
	

