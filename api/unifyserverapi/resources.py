from .db_init import Users, Events, Messages

from falcon_autocrud.resource import SingleResource, CollectionResource

class UserResource(SingleResource):
    model = Users
    response_fields = ['First_Name', 'Last_Name', 'Profile_Picture', 'Twitter_Link', 'Instagram_Link', 'Description', 'tags']

class UserCollectionResource(CollectionResource):
    model = Users
    methods = ['POST', 'PATCH']

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        print(dir(resource))

class EventResource(SingleResource):
    model = Events

class EventCollectionResource(CollectionResource):
    model = Events
    methods = ['POST', 'PATCH']

class MessageCollectionResource(CollectionResource):
    model = Messages
    methods = ['GET']