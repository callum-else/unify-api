import falcon
import json
import pymysql
from .utility import db_connect

class DBConnectionTest:
"""
Class for testing the connection to the Database from the scripts.
"""

    def on_get(self, req, resp):

        output = {
            'db_connected':False
        }

        connection = db_connect()

        try:
            output['db_connected'] = connection.open

        finally:
            connection.close()

        resp.body = json.dumps(output)
        


