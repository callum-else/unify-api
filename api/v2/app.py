import falcon

from .modules import DBConnectionTest, UserModule, EventModule

from falcon_autocrud.middleware import Middleware
from .middleware import CustomSessionManager

from .db_init import engine, Session, UserResource, EventResource

api = falcon.API(middleware=[
    CustomSessionManager(Session),
    Middleware(),
])

api.add_route('/test-db', DBConnectionTest())
api.add_route('/user/{User_ID}', UserResource(engine))
api.add_route('/event/{Event_ID}', EventResource(engine))