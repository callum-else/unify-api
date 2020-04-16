
######## FALCON-AUTOCRUD RESOURCE CREATION ########

# Relative resource imports.
from .db_init import (
    Users, UserTags, UserPictures, UserFriends, UserFriendRequests,
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
from bcrypt import gensalt, hashpw, checkpw

from sqlalchemy.exc import IntegrityError

# Image processing resource.
from mimetypes import guess_extension, guess_type
from uuid import uuid4
from os import makedirs, remove
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

# Template function for deleting items from a table.
def delete(session, table_object, error_obj, **kwargs):
        row = session.query(table_object).filter_by(**kwargs).scalar()

        if row is not None:
            session.delete(row)
        else:
            raise error_obj

def can_perform_action(req, User_ID):
    if req.context.user.User_ID is not User_ID:
        raise HTTPUnauthorized(
            'Cannot perform action.', 
            'Calling user does not have permission to perform requested action.'
        )

user_responses = ['User_ID', 'First_Name', 'Last_Name', 'Twitter_Link', 'Instagram_Link', 'Spotify_Link', 'LinkedIn_Link', 'Description']

# Single retrieval resource for editing, deleting and getting data from user profiles. 
class UserResource(SingleResource):
    model = Users       # Based off the 'Users' table in the db.
    response_fields = user_responses

    def before_patch(self, req, resp, db_session, resource, *args, **kwargs):
        can_perform_action(req, kwargs.get('User_ID'))
    
    def before_delete(self, req, resp, db_session, resource, *args, **kwargs):
        can_perform_action(req, kwargs.get('User_ID'))
    
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
                resource.Password = hashpw(bytes(resource.Password, 'utf-8'), gensalt())
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

class UserTagResource:

    def __init__(self):
        self._session_scope = session_scope

    def on_post(self, req, resp, User_ID):
        if int(User_ID) is req.context.user.User_ID:
            with self._session_scope() as db_session:
                new_tags = []
                if 'User_Tags' in req.context['doc']:
                    for tag in req.context['doc']['User_Tags']:
                        new_tags.append(
                            UserTags(
                                User_ID=req.context.user.User_ID,
                                User_Tag=str(tag)
                            )
                        )
                    db_session.add_all(new_tags)
                else:
                    # If data is missing, throw an error.
                    raise HTTPBadRequest(
                        "Information Invalid", 
                        "Provided information is incomplete."
                    )
    
    def on_delete(self, req, resp, User_ID):
        if int(User_ID) is req.context.user.User_ID:
            with self._session_scope() as db_session:
                req_info = dict(load(req.bounded_stream))
                if 'User_Tags' in req_info:
                    for tag in req_info['User_Tags']:
                        marked_tag = db_session.query(UserTags).filter_by(
                            User_ID=req.context.user.User_ID,
                            User_Tag=str(tag)
                        ).scalar()
                        if marked_tag is not None:
                            db_session.delete(marked_tag)
                else:
                    # If data is missing, throw an error.
                    raise HTTPBadRequest(
                        "Information Invalid", 
                        "Provided information is incomplete."
                    )

# Custom resource for creating, removing and accepting friend requests.
class UserFriendRequestResource:

    def __init__(self):
        self._session_scope = session_scope

    def on_post(self, req, resp, User_ID):
        if int(User_ID) is not req.context.user.User_ID:
            with self._session_scope() as db_session:
                reciever = user_loader({'user':{'User_ID':int(User_ID)}})
                if reciever is not None:
                    if req.context.user.User_ID not in (list(reciever.sent_requests) + list(reciever.recieved_requests)):
                        if req.context.user.User_ID not in (list(reciever.requested_friends) + list(reciever.recieved_friends)):
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
                                'Friendship already exists',
                                'A friendship already exists between the selected users.'
                            )
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
        else:
            raise HTTPBadRequest(
                'Cannot request self friendship.',
                'A user cannot request a friendship with themselves.'
            )
    
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
        with session_scope() as db_session:
            delete(
                db_session, 
                UserFriendRequests, 
                HTTPBadRequest(
                    "Friend Request Not Found", 
                    "Provided friend request has not been deleted as it could not be found."
                ),
                Sender_ID=req.context.user.User_ID,
                Reciever_ID=User_ID
            )

        resp.status = HTTP_200
        req.context['result'] = {}

# Custom resource for getting and deleting friendships.
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
    
    def on_delete(self, req, resp, User_ID):
        with session_scope() as db_session:
            Sender_ID = 0
            Reciever_ID = 0

            if User_ID in req.context.user.recieved_friends:
                Sender_ID = User_ID
                Reciever_ID = req.context.user.User_ID
            else:
                Sender_ID = req.context.user.User_ID
                Reciever_ID = User_ID
            
            delete(
                db_session, 
                UserFriends, 
                HTTPBadRequest(
                    "Friendship Not Found", 
                    "Provided friendship has not been deleted as it could not be found."
                ),
                User_ID=Reciever_ID,
                Friend_ID=Sender_ID
            )

        resp.status = HTTP_200
        req.context['result'] = {}

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
                user_temp = Session().query(Users).filter_by(
                    Email=user_info['Email']
                ).scalar()
                if user_temp is not None:
                    if checkpw(bytes(user_info['Password'], 'utf-8'), bytes(user_temp.Password, 'utf-8')):
                        user = user_temp
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

    # Information to return about the user.
    response_fields = user_responses

    def before_patch(self, req, resp, db_session, resource, *args, **kwargs):
        # User is authenticated and provided in the request context.
        user = req.context.user.User_ID

        # Comparing the client-sent verif code with the saved user verif code.
        # Sets the user to verified if they are the same, raises a Falcon Bad Request if not.
        if resource.Verification_Code is not None:
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

# Custom resource for processing, saving and returning images.
class ImageResource:

    _accepted_image_types = [
        'image/jpeg',
        'image/png'
    ]

    _max_image_size = (500, 500)

    def __init__(self, image_path):
        self._image_path = image_path
        self._session_scope = session_scope

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
                    title="Image Not Found", 
                    description="Requested image does not exist."
                )
        else:
            raise HTTPBadRequest(
                "Malformed Request", 
                "'user' and 'image' parameter not specified in request."
            )

    def on_delete(self, req, resp):
        if 'User_ID' in req.params and 'Picture_Path' in req.params:
            if int(req.params['User_ID']) is req.context.user.User_ID:
                with self._session_scope() as db_session:
                    image_path = validate_image_request(
                        join(self._image_path, req.params['User_ID']), 
                        req.params['Picture_Path']
                    )
                    if image_path is not None:
                        remove(image_path)
                        request = db_session.query(UserPictures).filter_by(
                            User_ID=req.params['User_ID'], 
                            Picture_Path=req.params['Picture_Path']
                        ).scalar()
                        if request is not None:
                            db_session.delete(request)
                    else:
                        raise HTTPNotFound(
                            title="Image Not Found", 
                            description="Requested image does not exist."
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
        
        with self._session_scope() as db_session:
            user_image = UserPictures(
                User_ID=req.context.user.User_ID,
                Picture_Path=file_name
            )
            db_session.add(user_image)

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

    def before_patch(self, req, resp, db_session, resource, *args, **kwargs):
        can_perform_action(req, resource.User_ID)
    
    def before_delete(self, req, resp, db_session, resource, *args, **kwargs):
        can_perform_action(req, resource.User_ID)

# Resource for getting a user's feed.
class EventFeedResource():
    model = Events
    methods = ['GET']

    def __init__(self):
        self._session_scope = session_scope

    # Limit & Offset
    def on_get(self, req, resp):
        with self._session_scope() as db_session:
            friends = set(
                list(req.context.user.recieved_friends) + 
                list(req.context.user.requested_friends)
            )
            
            db_session.query(Events).filter(
                Events.Event_ID.in_(
                    set(
                        db_session.query(EventUsers).filter(
                            EventUsers.User_ID.in_(friends)
                        ).all()
                    )
                )
            ).all()

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

# Resource for registering interest in events.
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

# Resource for reporting users for review.
class ReportUserResource(CollectionResource):
    model = ReportedUsers
    methods = ['POST']

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

# Resource for reporting events for review.
class ReportEventResource(CollectionResource):
    model = ReportedEvents
    methods = ['POST']

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
