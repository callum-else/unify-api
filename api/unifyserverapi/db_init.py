from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine, UniqueConstraint, Table, Column, String, ForeignKey

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

# Friends stored as one-to-many relationship, as is needed by SQLAlchemy
user_friends = Table('userfriends', Base.metadata,
    Column('User_ID', String(255), ForeignKey('users.User_ID'), index=True),
    Column('Friend_ID', String(255), ForeignKey('users.User_ID')),
    UniqueConstraint('User_ID', 'Friend_ID', name='Unique_Friendships'))

# Autoloading tables based on table names in the database.
# Additional relationships added as variabled in the table classes.

class EventUsers(Base):
    __tablename__ = 'eventsusers'
    __table_args__ = {'autoload':True, 'extend_existing':True}

# Relationship with user needs fixing, two references to the same table.
class Messages(Base):
    __tablename__ = 'usermessages'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class UserTags(Base):
    __tablename__ = 'usertags'
    __table_args__ = {'autoload':True, 'extend_existing':True}

class Events(Base):
    __tablename__ = 'events'
    __table_args__ = {'autoload':True, 'extend_existing':True}
    attendees = relationship('EventUsers', cascade='all, delete-orphan')

class Users(Base):
    __tablename__ = 'users'
    User_ID = Column(String(255), primary_key=True)
    __table_args__ = {'autoload':True, 'extend_existing':True}

    tags = relationship('UserTags', cascade='all, delete-orphan', backref='Users')
    events = relationship('EventUsers', cascade='all, delete-orphan',  backref='Users')
    friends = relationship('Users', secondary='userfriends', 
                            primaryjoin=User_ID==user_friends.c.User_ID, 
                            secondaryjoin=User_ID==user_friends.c.Friend_ID,
                            single_parent=True,
                            cascade='all')

###########################################################

# Session setup for SQLAlchemy Session creation.
Session = sessionmaker(
    bind=engine
)
