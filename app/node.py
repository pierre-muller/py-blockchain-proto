from app.restplus import api

#from app.blockchain import Blockchain
from flask_restplus import Resource, marshal_with, marshal
from app.parsers import registerPeer_args
from app.serializers import block

import requests
import sys

import logging

import json



class Node(object):
	class __Node(object):
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
				url="http://localhost:{}/api/acceptBlock/".format(peer)
				logging.debug("propagating block to peers, peer: {} block: {}".format(peer, json.dumps(marshal(newBlock, block))))
				headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
				ret = requests.post(url, data=json.dumps(marshal(newBlock, block)), headers=headers)
				logging.debug('response: {}'.format(ret.status_code))




	instance = None

	def __init__(self):
		if not Node.instance:
			Node.instance = Node.__Node()
	
	def __getattr__(self, name):
		return getattr(self.instance, name)

	def __setattr__(self, name):
		return setattr(self.instance, name)



