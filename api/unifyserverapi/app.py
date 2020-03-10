import falcon
from falcon_autocrud.middleware import Middleware
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend
from falcon_require_https import RequireHTTPS
from pem import parse_file

from .modules import DBConnectionTest

from .db_init import engine, Session
from .resources import UserResource, UserCollectionResource, EventResource, EventCollectionResource

# Setup for Authentication Middleware
# Rewrite to follow JWT user loader function requirements.
user_loader = lambda payload : payload
# cert = parse_file("")

# Falcon API initialisation, provided with Falcon middleware from imported modules.
api = falcon.API(middleware=[
    # RequireHTTPS(),
    Middleware(),
    FalconAuthMiddleware(JWTAuthBackend(user_loader, 'secret'))
])

# ============ Test Routes ============
api.add_route('/test-db', DBConnectionTest())

# ============ User Routes ============
api.add_route('/user/create/{User_ID}', UserCollectionResource(engine))
api.add_route('/user/{User_ID}', UserResource(engine))

# ============ Event Routes ===========
api.add_route('/event/create/{Event_ID}', EventCollectionResource(engine))
api.add_route('/event/{Event_ID}', EventResource(engine))