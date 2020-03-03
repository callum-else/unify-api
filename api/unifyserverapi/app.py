import falcon
from falcon_autocrud.middleware import Middleware

from .modules import DBConnectionTest

from .db_init import engine, Session
from .resources import UserResource, UserCollectionResource, EventResource, EventCollectionResource

# Falcon API initialisation, provided with Falcon_autocrud middleware.
api = falcon.API(middleware=[
    Middleware(),
])

# ============ Test Routes ============
api.add_route('/test-db', DBConnectionTest())

# ============ User Routes ============
api.add_route('/user/create/{User_ID}', UserCollectionResource(engine))
api.add_route('/user/{User_ID}', UserResource(engine))

# ============ Event Routes ===========
api.add_route('/event/create/{Event_ID}', EventCollectionResource(engine))
api.add_route('/event/{Event_ID}', EventResource(engine))