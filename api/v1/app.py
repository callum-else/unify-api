import falcon
from .modules import DBConnectionTest

api = falcon.API()
api.add_route('/test-db', DBConnectionTest())