
######## FALCON SETUP ########

# All falcon core and layer relevant imports
import falcon
from falcon_autocrud.middleware import Middleware
from falcon_auth import FalconAuthMiddleware
from falcon_require_https import RequireHTTPS

# Relative imports for developed functions.

# Custom authentication backend.
from .authentication import auth_backend
from .db_init import engine, Session, user_loader
from .resources import UserResource, UserCreationResource, UserLoginResource, UserVerificationResource, EventResource, EventCollectionResource

# Falcon API initialisation, provided with Falcon middleware from imported modules.
api = falcon.API(middleware=[
    # RequireHTTPS(),
    FalconAuthMiddleware(auth_backend),
    Middleware()
])

# ============ User Routes ============
api.add_route('/user/create', UserCreationResource(engine))
api.add_route('/user/{User_ID}/verify', UserVerificationResource(engine))
api.add_route('/user/{User_ID}', UserResource(engine))
api.add_route('/login', UserLoginResource())

# ============ Event Routes ===========
api.add_route('/event/create/{Event_ID}', EventCollectionResource(engine))
api.add_route('/event/{Event_ID}', EventResource(engine))