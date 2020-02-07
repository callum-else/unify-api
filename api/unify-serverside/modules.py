import falcon
import json
import pymysql.cursors

class test_db_connection:
"""
Class for testing the connection to the Database from the scripts.
"""

    def on_get(self, req, resp):

        output = {
            'resp':None
        }

        try:
            connection = pymysql.connect (
                host='localhost',
                port=3306,
                user='unify',
                password='V8oU!LkuYz',
                db='unify',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

            if connection.open:
                output['resp'] = "Connection Established."
            else:
                output['resp'] = "Connection Failed."

        finally:
            connection.close()

        resp.body = json.dumps(output)
        


