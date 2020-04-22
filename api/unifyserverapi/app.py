
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
from .resources import (
    UserResource, UserCreationResource, UserLoginResource, UserVerificationResource, 
    UserChangePasswordResource,
    UserFriendsResource, UserFriendRequestResource, UserFriendMatchResource,
    UserTagResource,
    EventResource, EventFeedResource, EventCreationResource, EventUsersResource, 
    ReportUserResource, ReportEventResource,
    ImageResource
)

# Falcon API initialisation, provided with Falcon middleware from imported modules.
api = falcon.API(middleware=[
    # RequireHTTPS(),
    FalconAuthMiddleware(auth_backend),
    Middleware()
])

# ============ User Routes ============
api.add_route('/login', UserLoginResource())
api.add_route('/user/create', UserCreationResource(engine))
api.add_route('/user/password/change', UserChangePasswordResource())
api.add_route('/user/{User_ID}', UserResource(engine))
api.add_route('/user/{User_ID}/tags', UserTagResource())
api.add_route('/user/{User_ID}/friends', UserFriendsResource())
api.add_route('/user/{User_ID}/friends/requests', UserFriendRequestResource())
api.add_route('/user/{User_ID}/verify', UserVerificationResource(engine))
api.add_route('/feed', EventFeedResource())
api.add_route('/matches', UserFriendMatchResource())

# ============ Event Routes ===========
api.add_route('/event/create', EventCreationResource(engine))
api.add_route('/event/{Event_ID}', EventResource(engine))
api.add_route('/event/{Event_ID}/users', EventUsersResource(engine))

# ============ Image Routes ===========
api.add_route('/images', ImageResource(
    r'C:\Users\cerle\Google Drive\_ University Work\Group Software Engineering\Project\unify-api\api\images\users')
)

# =========== Report Routes ===========
api.add_route('/report/user/{Reported_User_ID}', ReportUserResource(engine))
api.add_route('/report/event/{Reported_Event_ID}', ReportEventResource(engine))
