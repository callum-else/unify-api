from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, UniqueConstraint, Table, Column, String, ForeignKey

from falcon_autocrud.resource import SingleResource, CollectionResource

from .settings import db_settings

# Setup for the SQLAlchemy DB Engine, handles DB connection.

engine = create_engine(
    'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'.format(
        **db_settings
    )
)

# Setup for the SQLAlchemy DB Base that gathers information about the DB, used in declaration.

Base = declarative_base(engine)

###########################################################

# Database declaration for the SQLAlchemy ORM system.

user_friends = Table('userfriends', Base.metadata,
    Column('User_ID', String(255), ForeignKey('users.User_ID'), index=True),
    Column('Friend_ID', String(255), ForeignKey('users.User_ID')),
    UniqueConstraint('User_ID', 'Friend_ID', name='Unique_Friendships'))

class EventUsers(Base):
    __tablename__ = 'eventsusers'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class Messages(Base):
    __tablename__ = 'usermessages'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserTags(Base):
    __tablename__ = 'usertags'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class Events(Base):
    __tablename__ = 'events'
    __table_args__ = {'autoload':True, 'extend_existing':True}
    attendees = relationship('EventUsers')

class Users(Base):
    __tablename__ = 'users'
    User_ID = Column(String(255), primary_key=True)
    __table_args__ = {'autoload':True, 'extend_existing':True}

    tags = relationship('UserTags', backref='Users')
    events = relationship('EventUsers', backref='Users')
    friends = relationship('Users', secondary='userfriends', 
                            primaryjoin=User_ID==user_friends.c.User_ID, 
                            secondaryjoin=User_ID==user_friends.c.Friend_ID)
    messages = relationship('Messages', backref='Users')

###########################################################

class UserResource(SingleResource):
    model = Users
    response_fields = ['First_Name', 'Last_Name', 'Profile_Picture', 'Twitter_Link', 'Instagram_Link', 'Description']

class EventResource(SingleResource):
    model = Events

class EventCollectionResource(CollectionResource):
    model = Events
    methods = ['GET']

class MessageCollectionResource(CollectionResource):
    model = Messages
    methods = ['GET']

###########################################################

# Session setup for SQLAlchemy Session creation.

Session = sessionmaker(
    bind=engine
)
