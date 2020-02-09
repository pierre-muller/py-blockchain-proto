from flask_restplus import fields
from app.restplus import api


transaction = api.model('Transaction', {
    'fromAccount': fields.String(required=True),
    'toAccount' : fields.String(required=True),
    'amount': fields.Float(required=True)
})

block = api.model('Block', {
    'transactions': fields.List(fields.Nested(transaction), required=True),
    'index': fields.Integer(),
    'prevHash': fields.String(required=True),
    'ownHash': fields.String(required=True),
    'nounce': fields.Integer(required=True)

})


blockchain = api.model('Blockchain', {
    'blocks' : fields.List(fields.Nested(block), required=True)
    })

blockList = api.model('List of blocks', {
    'blocks' : fields.List(fields.Nested(block), required=True)
    })



accountBalance = api.model('AccountBalance', {
    'name': fields.String(required=True),
    'balance' : fields.Float(required=True)
    })

balances = api.model('Balances', {
    'accounts' : fields.List(fields.Nested(accountBalance), required=True)
    })


client = api.model('Client', {
    'name' : fields.String(required=True),
    'port' : fields.Integer(required=True),
    'honest' : fields.Boolean(required=True),
    'peers' : fields.List(fields.Integer(), required = True)
    })

"""
blog_post = api.model('Blog post', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a blog post'),
    'title': fields.String(required=True, description='Article title'),
    'body': fields.String(required=True, description='Article content'),
    'pub_date': fields.DateTime,
    'category_id': fields.Integer(attribute='category.id'),
    'category': fields.String(attribute='category.name'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_blog_posts = api.inherit('Page of blog posts', pagination, {
    'items': fields.List(fields.Nested(blog_post))
})

category = api.model('Blog category', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a blog category'),
    'name': fields.String(required=True, description='Category name'),
})

category_with_posts = api.inherit('Blog category with posts', category, {
    'posts': fields.List(fields.Nested(blog_post))
})
"""