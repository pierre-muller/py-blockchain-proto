from app.restplus import api
from app.serializers import blockchain, balances
from app.parsers import transaction_arguments
from flask_restplus import Resource, marshal_with, marshal
from app.client import Client
import hashlib

import json

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
		print("found nounce: {} giving hash value: {}".format(self.nounce, self.ownHash))
		

	def toJson(self):
		buf=json.dumps([ob.__dict__ for ob in self.transactions])
		buf='{"prevHash":"' + self.prevHash + '", "nounce":"' + str(self.nounce) + '","index":"' + str(self.index) + '", "transactions":' + buf + '}'
		return buf
		





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
		block.addTransaction("pierre","pierre",1000)
		block.mine()
		self.blocks.append(block)

	def addTransaction(self, fromAccount, toAccount, amount):
	
		prevBlock = self.blocks[-1]
		block = Block(prevBlock.index + 1, prevBlock.ownHash)
		block.addTransaction(fromAccount, toAccount, amount)
		block.mine()
		self.blocks.append(block)

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


@ns_blockchain.route('/sendTransaction')
class sendTransaction(Resource):

	@api.expect(transaction_arguments)
	def post(self):

		args = transaction_arguments.parse_args()
		balances = appBlockhain.getBalances()
		if args['fromAccount'] not in balances or balances[args['fromAccount']] < args['amount']:
			return "Insufficient funds", 403

		Client.instance.blockchain.addTransaction(args['fromAccount'], args['toAccount'], args['amount'])

		return "Done", 201