
######## FALCON-AUTOCRUD RESOURCE CREATION ########

# Relative resource imports.
from .db_init import (
    Users, UserTags, UserFriends, UserFriendRequests,
    Events, EventUsers, 
    ReportedEvents, ReportedUsers,
    user_loader, Session
)
from .authentication import (
    auth_backend, 
    generate_verification_code, send_verification_email, check_valid_email, 
    validate_image_request
)

# Falcon resource imports.
from falcon_autocrud.resource import SingleResource, CollectionResource
from falcon import (
    HTTPBadRequest, HTTPUnauthorized, HTTPNotFound, HTTPConflict,
    HTTP_201, HTTP_200
)

from json import load
from jwt import decode

from sqlalchemy.exc import IntegrityError

# Image processing resource.
from mimetypes import guess_extension, guess_type
from uuid import uuid4
from os import makedirs
from os.path import join, exists, getsize
from io import open, BytesIO
from PIL import Image

# Custom Session Manager.
from contextlib import contextmanager

@contextmanager
def session_scope():
    db_session = Session()
    try:
        yield db_session
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

# Function for adding user relationship data.
def get_user_rels(user):
    return {
        'tags':list(user.tags),
        'pictures':list(user.pictures),
        'events':list(user.events),
        'friends':list(user.recieved_friends) + list(user.requested_friends)
    }

user_responses = ['User_ID', 'First_Name', 'Last_Name', 'Twitter_Link', 'Instagram_Link', 'Spotify_Link', 'LinkedIn_Link', 'Description']

# Single retrieval resource for editing, deleting and getting data from user profiles. 
class UserResource(SingleResource):
    model = Users       # Based off the 'Users' table in the db.
    response_fields = user_responses

    def before_patch(self, req, resp, db_session, resource, *args, **kwargs):
        pass
    
    def after_get(self, req, resp, item, *args, **kwargs):
        req.context['result']['data'].update(get_user_rels(item))

# Collection posting resource for uploading profiles.
class UserCreationResource(CollectionResource):
    model = Users
    methods = ['POST']

    allow_subresources = True
    response_fields = user_responses

    # No authentication needed for profile creation.
    auth = {
        'auth_disabled': True
    }

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        # If the user email is valid, set them a verif code.
        # If not, raise a Falcon Unauthorized error.
        if check_valid_email(resource.Email):
            if db_session.query(Users).filter_by(Email=resource.Email).scalar() is None:
                resource.Verification_Code = generate_verification_code()
            else:
                raise HTTPBadRequest(
                    "Email already exists", 
                    "A user already exists with this email."
                )
        else:
            raise HTTPUnauthorized(
                "Not an Acedemic Email", 
                "Provided email address is not an acedemic email."
            )

    def after_post(self, req, resp, new, *args, **kwargs):
        # If the user passes all the checks, send them an email and return a JWT token to them.
        send_verification_email(new.Email, new.First_Name, new.Verification_Code)
        # JWT RETURNED TO USER for user request authentication.
        req.context['result']['access_token'] = auth_backend.get_auth_token({'User_ID':new.User_ID})
        req.context['result']['data'].update(get_user_rels(new))
        
class UserFriendsResource:

    def __init__(self):
        self._session_scope = session_scope

    def on_get(self, req, resp, User_ID):
        with self._session_scope() as db_session:
            user = user_loader({'user':{'User_ID':int(User_ID)}})
            req.context['result'] = {
                'data': { 
                    'friends': list(user.recieved_friends) + list(user.requested_friends)
                }
            }

    def on_post(self, req, resp, User_ID):
        with self._session_scope() as db_session:
            reciever = user_loader({'user':{'User_ID':int(User_ID)}})
            if reciever is not None:
                if req.context.user.User_ID not in (list(reciever.sent_requests) + list(reciever.recieved_requests)): 
                    request = UserFriendRequests(
                        Reciever_ID=int(User_ID), 
                        Sender_ID=req.context.user.User_ID
                    )
                    db_session.add(request)
                    req.context['result'] = {
                        'data': {
                            'sender': req.context.user.User_ID,
                            'reciever': int(User_ID)
                        }
                    }
                else:
                    raise HTTPConflict(
                        'Request already exists',
                        'A friend request has already been sent between selected users.'
                    )
            else:
                raise HTTPBadRequest(
                    'User not found',
                    'The requested user does not exist.'
                )
        
        req.status = HTTP_200
    
    def on_patch(self, req, resp, User_ID):
        with self._session_scope() as db_session:
            request = db_session.query(UserFriendRequests).filter_by(
                Sender_ID=User_ID, 
                Reciever_ID=req.context.user.User_ID
            ).scalar()
            if request is not None:
                db_session.delete(request)
                friendship = UserFriends(
                    User_ID=req.context.user.User_ID,
                    Friend_ID=int(User_ID)
                )
                db_session.add(friendship)
                req.context['result'] = {
                    'data': {
                        'sender': int(User_ID),
                        'accepted': req.context.user.User_ID
                    }
                }
            else:
                raise HTTPBadRequest(
                    'Request not found',
                    'A friend request between the requested users does not exist.'
                )


    def on_delete(self, req, resp, User_ID):
        pass

# Custom built login resource.
class UserLoginResource:
    """
    Login Resource.

    Logs a user into the system using the 'GET' method.
    For manual login, send 'Email' and 'Password' in the body of the request.
    For automatic login  (When re-opening the application), send the same request with a valid Authentication Header. 
    """

    # Information to return about the user.
    response_fields = user_responses
    
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
                raise HTTPBadRequest(
                    "Information Invalid", 
                    "Provided information is incomplete."
                )

        # If the user exists, return an auth token and all the info listed in response_fields.
        if(user is not None):
            req.context['result'] = {
                'access_token': auth_backend.get_auth_token({'User_ID':user.User_ID}),
                'data': {}
            }
            for field in self.response_fields:
                req.context['result']['data'][field] = getattr(user, field)
            req.context['result']['data'].update(get_user_rels(user))
        else:
            # If the user does not exist, throw an error.
            raise HTTPUnauthorized(
                "Invalid Username or Password", 
                "Provided Username or Password is incorrect."
            )

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
                raise HTTPBadRequest(
                    "Invalid Verification Code", 
                    "Provided code does not match the required user verification code."
                )
        else:
            raise HTTPBadRequest(
                "No Verification Code", 
                "No user verification code was sent, but it is required."
            )

class ImageResource:

    _accepted_image_types = [
        'image/jpeg',
        'image/png'
    ]

    _max_image_size = (500, 500)

    def __init__(self, image_path, chunk_size_bytes=4096):
        
        self._image_path = image_path
        self._chunk_size_bytes = chunk_size_bytes

    def on_get(self, req, resp):
        if 'user' in req.params and 'image' in req.params:
            image_path = validate_image_request(
                join(self._image_path, req.params['user']), 
                req.params['image']
            )
            if image_path is not None:
                resp.stream = open(image_path, 'rb')
                resp.content_length = getsize(image_path)
                resp.content_type = guess_type(req.params['image'])[0]
            else:
                raise HTTPNotFound(
                    "Image Not Found", 
                    "Requested image does not exist at destination: /images/{user}/{image_name}".format(
                        user=req.params['user'], 
                        image_name=req.params['image']
                    )
                )
        else:
            raise HTTPBadRequest(
                "Malformed Request", 
                "'user' and 'image' parameter not specified in request."
            )

    def on_post(self, req, resp):

        if req.content_type not in self._accepted_image_types:
            raise HTTPBadRequest('Image not accepted', 'Image was not of the correct file type.')

        image_folder = join(self._image_path, str(req.context.user.User_ID))
        if not exists(image_folder): makedirs(image_folder)
        
        file_name = '{id}.jpg'.format(id=uuid4())
        image_path = join(image_folder, file_name)

        image_obj = self.format_image(Image.open(req.stream), req.get_param_as_list('crop_boundary', transform=int))

        image_obj.save(image_path, 'JPEG', optimize=True, quality=80)
        image_obj.close()
        
        resp.status = HTTP_201
        req.context['result'] = {
            'data': {
                'user':req.context.user.User_ID, 
                'image':file_name
            }
        }

    def format_image(self, image_obj, crop_boundary_list):
        if crop_boundary_list is not None:
            image_obj.crop(tuple(crop_boundary_list))

        elif image_obj.size[0] != image_obj.size[1]:
            crop_area = (
                0, (image_obj.size[1]/2) - (image_obj.size[0]/2),                   # X, Y for the top left coord.
                image_obj.size[0], (image_obj.size[1]/2) + (image_obj.size[0]/2)    # X, Y for the bottom right coord.
            ) if image_obj.size[1] > image_obj.size[0] else (
                (image_obj.size[0]/2) - (image_obj.size[1]/2), 0,                   # X, Y for the top left coord.
                (image_obj.size[0]/2) + (image_obj.size[1]/2), image_obj.size[1]    # X, Y for the bottom right coord.
            )

            image_obj = image_obj.crop(crop_area)

        if image_obj.size[0] > self._max_image_size[0]:
            image_obj = image_obj.resize(self._max_image_size)
        
        if any(x in image_obj.getbands() for x in ['A', 'a']):
            image_obj = image_obj.convert('RGB')
        
        return image_obj

# Event resource for getting, deleting and editing single events.
class EventResource(SingleResource):
    model = Events

# Event resource for uploading and editing resources.
class EventCreationResource(CollectionResource):
    model = Events
    methods = ['POST', 'PATCH']

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        resource.User_ID = req.context.user.User_ID

    def after_post(self, req, resp, new, *args, **kwargs):
        with session_scope() as db_session:
            event_user = EventUsers(Event_ID=new.Event_ID, User_ID=new.User_ID)
            db_session.add(event_user)

class EventUsersResource(CollectionResource):
    model = EventUsers
    methods = ['POST', 'GET']

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        resource.User_ID = req.context.user.User_ID

    def on_delete(self, req, resp, Event_ID):
        with session_scope() as db_session:
            delete(
                db_session, 
                EventUsers, 
                HTTPBadRequest(
                    "User Not Found", 
                    "Provided user does not exist in this event."
                ),
                User_ID=req.context.user.User_ID,
                Event_ID=Event_ID
            )
        
        resp.status = HTTP_200
        req.context['result'] = {}

class ReportUserResource(CollectionResource):
    model = ReportedUsers

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        resource.Reporting_User_ID = req.context.user.User_ID
        if 'Reported_User_ID' in kwargs:
            if user_loader({'user':{'User_ID':kwargs.get('Reported_User_ID')}}) is None:
                raise HTTPBadRequest(
                    'User does not exist', 
                    'The reported user does not exist.'
                )
        else:
            raise HTTPBadRequest(
                'User not provided',
                'Report request could not be completed as no user was provided.'
            )

    def on_delete(self, req, resp, User_ID):
        with session_scope() as db_session:
            delete(
                db_session, 
                ReportedUsers, 
                HTTPBadRequest(
                    "User Not Found", 
                    "Provided user has not been reported."
                ),
                Reporting_User_ID=req.context.user.User_ID,
                Reported_User_ID=User_ID
            )
        
        resp.status = HTTP_200
        req.context['result'] = {}

class ReportEventResource(CollectionResource):
    model = ReportedEvents

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        resource.Reporting_User_ID = req.context.user.User_ID
        if 'Reported_Event_ID' in kwargs:
            if db_session.query(Events).filter_by(Event_ID=kwargs.get('Reported_Event_ID')).scalar() is None:
                raise HTTPBadRequest(
                    'Event does not exist', 
                    'The reported event does not exist.'
                )
        else:
            raise HTTPBadRequest(
                'Event not provided',
                'Report request could not be completed as no event was provided.'
            )
            

    def on_delete(self, req, resp, Event_ID):
        with session_scope() as db_session:
            delete(
                db_session, 
                ReportedUsers, 
                HTTPBadRequest(
                    "Event Not Found", 
                    "Provided event has not been reported."
                ),
                Reporting_User_ID=req.context.user.User_ID,
                Reported_Event_ID=Event_ID
            )
        
        resp.status = HTTP_200
        req.context['result'] = {}

def delete(session, table_object, error_obj, **kwargs):
        row = session.query(table_object).filter_by(**kwargs).scalar()

        if row is not None:
            session.delete(row)
        else:
            raise error_obj
