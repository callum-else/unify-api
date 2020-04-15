from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine, UniqueConstraint, Table, Column, String, Integer, ForeignKey

db_settings = {
    'host':'localhost',
    'port':3306,
    'user':'unify',
    'password':'V8oU!LkuYz',
    'db':'unify'
}

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

# Friends stored as one-to-many relationship, as is needed by SQLAlchemy
user_friends = Table('userfriends', Base.metadata,
    Column('User_ID', Integer, ForeignKey('users.User_ID'), index=True),
    Column('Friend_ID', Integer, ForeignKey('users.User_ID')),
    UniqueConstraint('User_ID', 'Friend_ID', name='Unique_Friendships'))

# Autoloading tables based on table names in the database.
# Additional relationships added as variabled in the table classes.

# Relationship with user needs fixing, two references to the same table.
class ReportedUsers(Base):
    __tablename__ = 'reportedusers'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class ReportedEvents(Base):
    __tablename__ = 'reportedevents'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class EventUsers(Base):
    __tablename__ = 'eventsusers'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserTags(Base):
    __tablename__ = 'usertags'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserPictures(Base):
    __tablename__ = 'userpictures'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserFriends(Base):
    __tablename__ = 'userfriends'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserFriendRequests(Base):
    __tablename__ = 'userfriendrequests'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class Events(Base):
    __tablename__ = 'events'
    __table_args__ = {'autoload':True, 'extend_existing':True}
    attendees = relationship('EventUsers', cascade='all, delete-orphan')

class Users(Base):
    __tablename__ = 'users'
    User_ID = Column(Integer, primary_key=True)
    __table_args__ = {'autoload':True, 'extend_existing':True}

    tag_rels = relationship('UserTags', cascade='all, delete-orphan', backref='tag_user')
    tags = association_proxy('tag_rels', 'User_Tag')

    picture_rels = relationship('UserPictures', cascade='all, delete-orphan', backref='picture_owner')
    pictures = association_proxy('picture_rels', 'Picture_Path')

    event_rels = relationship('EventUsers', cascade='all, delete-orphan',  backref='event_users')
    events = association_proxy('event_rels', 'Event_ID')

    requested_friend_rels = relationship('UserFriends', foreign_keys='UserFriends.User_ID', backref='requested_user', cascade='all, delete-orphan')
    requested_friends = association_proxy('requested_friend_rels', 'Friend_ID')

    recieved_friend_rels = relationship('UserFriends', foreign_keys='UserFriends.Friend_ID', backref='recieved_user', cascade='all, delete-orphan')
    recieved_friends = association_proxy('recieved_friend_rels', 'User_ID')

    sent_request_rels = relationship('UserFriendRequests', foreign_keys='UserFriendRequests.Sender_ID', backref='sent_requests', cascade='all, delete-orphan')
    sent_requests = association_proxy('sent_request_rels', 'Sent_ID')

    recieved_request_rels = relationship('UserFriendRequests', foreign_keys='UserFriendRequests.Reciever_ID', backref='recieved_requests', cascade='all, delete-orphan')
    recieved_requests = association_proxy('recieved_request_rels', 'Reciever_ID')

###########################################################

# Session setup for SQLAlchemy Session creation.
Session = sessionmaker(
    bind=engine
)

###########################################################

def user_loader(payload):
    user = Session().query(Users).filter_by(User_ID=payload["user"]["User_ID"]).scalar()
    if user is not None:
        return user
    else:
        return None
