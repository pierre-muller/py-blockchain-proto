from app.restplus import api

#from app.blockchain import Blockchain
from flask_restplus import Resource, marshal_with, marshal
from app.serializers import client, blockList, block
from app.parsers import registerPeer_args

import requests
import sys

import logging

import json




ns_client = api.namespace('client', description='Operations related to the client')

class Client(object):
	class __Client(object):
		port = 8888
		name = ""
		honest = True
		peers = set()
		def __init__(self):
			self.peers = []
			from app.blockchain import Blockchain
			self.blockchain = Blockchain()
			self.rejectedBlocks = []


		def registerPeer(self, peer):
			if (peer != self.port) and (peer not in self.peers):
				self.peers.append(peer)

		def propagateBlockToPeers(self, newBlock):
			from app.blockchain import Block
			logging.debug("Propagating block: {}".format(marshal(newBlock, block)))
			for peer in self.peers:
				url="http://localhost:{}/api/blockchain/acceptBlock/".format(peer)
				logging.debug("propagating block to peers, peer: {} block: {}".format(peer, json.dumps(marshal(newBlock, block))))
				headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
				ret = requests.post(url, data=json.dumps(marshal(newBlock, block)), headers=headers)
				logging.debug('response: {}'.format(ret.status_code))




	instance = None

	def __init__(self):
		if not Client.instance:
			Client.instance = Client.__Client()
	
	def __getattr__(self, name):
		return getattr(self.instance, name)

	def __setattr__(self, name):
		return setattr(self.instance, name)





@ns_client.route('/')
class ClientEndpoint(Resource):

	@api.marshal_with(client)
	def get(self):
		return Client().instance, 200


@ns_client.route('/registerPeer/')
class RegisterPeer(Resource):

	@api.expect(registerPeer_args)
	def post(self):
		args = registerPeer_args.parse_args()

		Client.instance.registerPeer(args['peer'])


		return "Registered peer: {} ".format(args['peer']), 201

@ns_client.route('/rejectedBlocks/')
class getRejectedBlocks(Resource):

	@api.marshal_with(block)
	def get(self):
		return Client.instance.rejectedBlocks, 200

