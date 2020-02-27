import falcon
import json
import pymysql

# Import for SQLAlchemy
# from .utility import session_scope

from .utility import db_connect

class DBConnectionTest:
    """
        Class for testing the connection to the Database from the scripts.
    """

    def on_get(self, req, resp):

        output = {
            'db_connected':False
        }

        with db_connect().cursor as cursor:
            try:
                output['db_connected'] = cursor.open
            finally:
                cursor.close()

        # with session_scope() as session:
        #     try:
        #         output['db_connected'] = session.is_active
        #     finally:
        #         session.close()

        resp.body = json.dumps(output)
        
# class User:

#     def on_get(self, req, resp, user_id):
#         output = {}

#         with session_scope() as session:
#             try:
#                 session.query(users)
        

