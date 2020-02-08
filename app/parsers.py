from flask_restplus import reqparse

transaction_arguments = reqparse.RequestParser()
transaction_arguments.add_argument('fromAccount', type=str, required=True)
transaction_arguments.add_argument('toAccount', type=str, required=True)
transaction_arguments.add_argument('amount', type=float, required=True)


registerPeer_args = reqparse.RequestParser()
registerPeer_args.add_argument('peer', type=int, required=True)