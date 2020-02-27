import falcon

from .modules import DBConnectionTest, UserModule, EventModule
from .middleware import CustomSessionManager
from .db_init import Session

api = falcon.API(middleware=[
    CustomSessionManager(Session),
])

api.add_route('/test-db', DBConnectionTest())
api.add_route('/user/{user_id:uuid}', UserModule())
api.add_route('/event/{event_id:uuid}', EventModule())