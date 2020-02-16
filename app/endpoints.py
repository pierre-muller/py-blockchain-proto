from app.restplus import api

#from app.blockchain import Blockchain
from flask_restplus import Resource, marshal_with, marshal
from app.serializers import node, blockList, block, blockchain, balances
from app.parsers import registerPeer_args, transaction_arguments

from app.blockchain import Block, Blockchain, Accounts, Account
from app.node import Node

import logging


from flask import request

ns_operations = api.namespace('', description='Node operations')



@ns_operations.route('/nodeInfo')
class NodeInfo(Resource):

	@api.marshal_with(node)
	def get(self):
		return Node.instance, 200


@ns_operations.route('/registerPeer/')
class RegisterPeer(Resource):

	@api.expect(registerPeer_args)
	def post(self):
		args = registerPeer_args.parse_args()

		Node.instance.registerPeer(args['peer'])


		return "Registered peer: {} ".format(args['peer']), 201

@ns_operations.route('/rejectedBlocks/')
class getRejectedBlocks(Resource):

	@api.marshal_with(block)
	def get(self):
		return Node.instance.rejectedBlocks, 200






@ns_operations.route('/blockchain/')
class BlockchainEndpoint(Resource):


	@api.marshal_with(blockchain)
	def get(self):
		return Node.instance.blockchain, 200

@ns_operations.route('/balances')
class balances(Resource):

	@api.marshal_with(balances)
	def get(self):
		bal = Node.instance.blockchain.getBalances()
		acc = Accounts()
		for name in bal:
			acc.accounts.append(Account(name, bal[name]))
		return acc, 200


@ns_operations.route('/sendTransaction/')
class sendTransaction(Resource):

	@api.expect(transaction_arguments)
	def post(self):

		args = transaction_arguments.parse_args()
		balances = Node.instance.blockchain.getBalances()
		if (args['fromAccount'] not in balances or balances[args['fromAccount']] < args['amount']) and Node.instance.honest:
			return "Insufficient funds", 403

		newBlock = Node.instance.blockchain.createNewBlock()
		newBlock.addTransaction(args['fromAccount'], args['toAccount'], args['amount'])
		newBlock.mine()
		Node.instance.blockchain.blocks.append(newBlock)
		if not Node.instance.blockchain.isLastBlockValid() and Node.instance.honest:
			Node.instance.blockchain.blocks.pop()
			return "Insufficient funds", 403

		# forward new block to peers
		Node.instance.propagateBlockToPeers(newBlock)


		return "Done", 201


@ns_operations.route('/acceptBlock/')
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

			Node.instance.blockchain.blocks.append(newBlock)

			logging.debug("Try accepting block")
			logging.debug(Node.instance.blockchain.getBalances())
			if Node.instance.blockchain.isLastBlockValid():
				return "Accepted", 201

			else:
				Node.instance.blockchain.blocks.pop()
				Node.instance.rejectedBlocks.append(newBlock)
				return "Rejected", 403
		except:
			logging.exception("Unexpected error")
			return "Unexpected error", 500

@ns_operations.route('/isChainValid/')
class isChainValid(Resource):
	def get(self):
		return Node.instance.blockchain.isFullChainValid(), 200