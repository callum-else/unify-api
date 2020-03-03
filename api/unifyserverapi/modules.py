import falcon
import json
import pymysql

class DBConnectionTest:
    """
        Class for testing the connection to the Database from the scripts.
    """

    def on_get(self, req, resp):

        output = {
            'db_connected':False
        }

        if req.context.get('db_session') and req.context['db_session'].is_active:
            output['db_connected'] = True

        resp.body = json.dumps(output)

