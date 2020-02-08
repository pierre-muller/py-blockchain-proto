from app.restplus import api

#from app.blockchain import Blockchain
from flask_restplus import Resource, marshal_with, marshal
from app.serializers import client



ns_client = api.namespace('client', description='Operations related to the client')

class Client(object):
	class __Client(object):
		port = 8888
		name = ""
		honest = True
		peers = []
		def __init__(self):
			self.peers = []
			from app.blockchain import Blockchain
			self.blockchain = Blockchain()

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
		return marshal(Client().instance, client), 200
