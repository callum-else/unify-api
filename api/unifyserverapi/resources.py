
######## FALCON-AUTOCRUD RESOURCE CREATION ########

# Relative resource imports.
from .db_init import Users, Events, UserTags, user_loader, Session
from .authentication import auth_backend, generate_verification_code, send_verification_email, check_valid_email

# Falcon resource imports.
from falcon_autocrud.resource import SingleResource, CollectionResource
from falcon import HTTPBadRequest, HTTPUnauthorized

from json import load
from jwt import decode

# Single retrieval resource for editing, deleting and getting data from user profiles. 
class UserResource(SingleResource):
    model = Users       # Based off the 'Users' table in the db.
    response_fields = ['User_ID', 'First_Name', 'Last_Name', 'Twitter_Link', 'Instagram_Link', 'Description', 'tags']

# Single patching resource for account verification.
class UserVerificationResource(SingleResource):
    model = Users
    methods = ['PATCH']

    def before_patch(self, req, resp, db_session, resource, *args, **kwargs):
        # User is authenticated and provided in the request context.
        user = req.context.user.User_ID

        # Comparing the client-sent verif code with the saved user verif code.
        # Sets the user to verified if they are the same, raises a Falcon Bad Request if not.
        if getattr(resource.Verification_Code) is not None:
            if resource.Verification_Code == str(req.context.user.Verification_Code):
                resource.User_Verified = True
            else:
                raise HTTPBadRequest("Invalid Verification Code", "Provided code does not match the required user verification code.")
        else:
            raise HTTPBadRequest("No Verification Code", "No user verification code was sent, but it is required.")

# Collection posting resource for uploading profiles.
class UserCreationResource(CollectionResource):
    model = Users
    methods = ['POST']

    response_fields = ['User_ID', 'First_Name', 'Last_Name', 'Twitter_Link', 'Instagram_Link', 'Description', 'tags']

    # No authentication needed for profile creation.
    auth = {
        'auth_disabled': True
    }

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        # If the user email is valid, set them a verif code.
        # If not, raise a Falcon Unauthorized error.
        if check_valid_email(resource.Email):
            if Session().query(Users).filter_by(Email=resource.Email).scalar() is None:
                resource.Verification_Code = generate_verification_code()
            else:
                raise HTTPBadRequest("Email already exists", "A user already exists with this email.")
        else:
            raise HTTPUnauthorized("Not an Acedemic Email", "Provided email address is not an acedemic email.")

    def after_post(self, req, resp, new, *args, **kwargs):
        # If the user passes all the checks, send them an email and return a JWT token to them.
        send_verification_email(new.Email, new.First_Name, new.Verification_Code)
        # JWT RETURNED TO USER for user request authentication.
        req.context['result']['access_token'] = auth_backend.get_auth_token({'User_ID':new.User_ID})
        
# Custom built login resource.
class UserLoginResource:
    """
    Login Resource.

    Logs a user into the system using the 'GET' method.
    For manual login, send 'Email' and 'Password' in the body of the request.
    For automatic login  (When re-opening the application), send the same request with a valid Authentication Header. 
    """

    # Information to return about the user.
    response_fields = ['User_ID', 'First_Name', 'Last_Name', 'Twitter_Link', 'Instagram_Link', 'Description', 'tags']
    
    # No authentication needed for user login.
    auth = {
        'auth_disabled': True
    }

    # Login request sent through the 'GET' action.
    def on_get(self, req, resp):
        user = None

        # Checks if an authorized request has been made.
        # Tests if the JWT token is valid, and returns a user.
        if req.get_header('Authorization') is not None:
            user = auth_backend.authenticate(req, None, None)
        else:
            # Loading user login info from the request and tests if the correct information was passed.
            user_info = dict(load(req.bounded_stream))
            if 'Email' in user_info and 'Password' in user_info and check_valid_email(user_info['Email']):
                # SQLAlchemy session db query for returning a user object with input Email and Password, returns none if not found.
                user = Session().query(Users).filter_by(Email=user_info['Email'], Password=user_info['Password']).scalar()
            else:
                # If data is missing, throw an error.
                raise HTTPBadRequest("Information Invalid", "Provided information is incomplete.")

        # If the user exists, return an auth token and all the info listed in response_fields.
        if(user is not None):
            req.context['result'] = {
                'access_token': auth_backend.get_auth_token({'User_ID':user.User_ID}),
                'data': {}
            }
            for field in self.response_fields:
                req.context['result']['data'][field] = getattr(user, field)
        else:
            # If the user does not exist, throw an error.
            raise HTTPUnauthorized("Invalid Username or Password", "Provided Username or Password is incorrect.")

# Event resource for getting, deleting and editing single events.
class EventResource(SingleResource):
    model = Events

# Event resource for uploading and editing resources.
class EventCollectionResource(CollectionResource):
    model = Events
    methods = ['POST', 'PATCH']
