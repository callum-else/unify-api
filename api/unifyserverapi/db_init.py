from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
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
    Column('User_ID', String(255), ForeignKey('users.User_ID'), index=True),
    Column('Friend_ID', String(255), ForeignKey('users.User_ID')),
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

class Events(Base):
    __tablename__ = 'events'
    __table_args__ = {'autoload':True, 'extend_existing':True}
    attendees = relationship('EventUsers', cascade='all, delete-orphan')

class Users(Base):
    __tablename__ = 'users'
    User_ID = Column(Integer, primary_key=True)
    __table_args__ = {'autoload':True, 'extend_existing':True}

    tags = relationship('UserTags', cascade='all, delete-orphan', backref='Users')
    pictures = relationship('UserPictures', cascade='all, delete-orphan', backref='Users')
    events = relationship('EventUsers', cascade='all, delete-orphan',  backref='Users')
    friends = relationship('Users', secondary='userfriends', 
                            primaryjoin=User_ID==user_friends.c.User_ID, 
                            secondaryjoin=User_ID==user_friends.c.Friend_ID,
                            single_parent=True,
                            cascade='all, delete-orphan')

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
