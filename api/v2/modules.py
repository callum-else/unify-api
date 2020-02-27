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

class UserModule:
    """
    """

    def on_get(self, req, resp, user_id):
        pass

    def on_post(self, req, resp, user_id):
        if req.context.get('db_session'):
            if 'user' in req.body:
                pass

            

    def on_put(self, req, resp, user_id):
        pass

    def on_delete(self, req, resp, user_id):
        pass

class EventModule:
    """
    """

    def on_get(self, req, resp, user_id):
        pass

    def on_post(self, req, resp, user_id):
        pass

    def on_put(self, req, resp, user_id):
        pass

    def on_delete(self, req, resp, user_id):
        pass

