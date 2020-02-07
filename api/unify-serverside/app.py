import falcon
from .modules import test_db_connection

api = falcon.API()
api.add_route('/test', test_db_connection())