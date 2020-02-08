from app.restplus import api

#from app.blockchain import Blockchain
from flask_restplus import Resource, marshal_with, marshal
from app.serializers import client
from app.parsers import registerPeer_args



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


		def registerPeer(self, peer):
			if peer != self.port and peer not in self.peers:
				self.peers.append(peer)

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


@ns_client.route('/registerPeer')
class RegisterPeer(Resource):

	@api.expect(registerPeer_args)
	def post(self):
		args = registerPeer_args.parse_args()
		Client.instance.registerPeer(args['peer'])
		return "Registered peer: {}".format(args['peer']), 201
