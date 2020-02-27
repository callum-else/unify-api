from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Table, ForeignKeyConstraint, UniqueConstraint, Column, String, CHAR, DateTime, Date, DECIMAL

# Database connection settings.
user = 'unify'
password = 'V8oU!LkuYz'
host = 'localhost'
db = 'unify'
port = 3306

# Setting up an automapped base for auto-generated table objects.
Base = declarative_base()

# Creating an SQLAlchemy Engine to connect to the database.
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}')

# Base.prepare(engine, reflect=True)

# Creating a session base with sessionmaker to handle database sessions.
# Allows for the temporary manipulation of the database with the option to rollback.
Session = sessionmaker(bind=engine)

userFriends = Table(
    'userfriends', Base.metadata,
    Column('User_ID', String(255), nullable=False),
    Column('Friend_ID', String(255), nullable=False),
    __table_args__ = (
        ForeignKeyConstraint(["User_ID"], ["users.User_ID"]),
        ForeignKeyConstraint(["Friend_ID"], ["users.User_ID"]),
        UniqueConstraint('User_ID', 'Friend_ID', name='friendship'),
    )
)

class Users(Base):
    __tablename__ = "users"
    User_ID = Column(String(255), nullable=False, primary_key=True)
    Email = Column(String(40), nullable=False)
    First_Name = Column(CHAR(60), nullable=False)
    DateOfBirth = Column(Date(), nullable=False)
    Password = Column(String(64), nullable=False)
    Profile_Picture = Column(String(255), nullable=True)
    Twitter_Link = Column(String(255), nullable=True)
    Instagram_Link = Column(String(255), nullable=True)
    Description = Column(String(255), nullable=True)
    User_Created = Column(DateTime(), nullable=False)
    Last_Login = Column(DateTime(), nullable=False)
    Tags = relationship("UserTags")
    Friends = relationship("Users", secondary=userFriends)
    Messages = relationship("UserMessages")
    Events = relationship("EventUsers")

class UserMessages(Base):
    __tablename__ = "usermessages"
    User_Sent = Column(String(255), nullable=False)
    User_Recieved = Column(String(255), nullable=False)
    Message_ID = Column(String(255), nullable=False, primary_key=True)
    Message = Column(String(255), nullable=False)
    Sent_DateTime = Column(DateTime(), nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(["User_Sent"], ["users.User_ID"]),
        ForeignKeyConstraint(["User_Recieved"], ["users.User_ID"]),
    )

class UserTags(Base):
    __tablename__ = "usertags"
    User_ID = Column(String(255), nullable=False, primary_key=True)
    User_Tag = Column(String(255), nullable=False, primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint(["User_ID"], ["users.User_ID"]),
    )

class Events(Base):
    __tablename__ = "events"
    Event_ID = Column(String(255), nullable=False, primary_key=True)
    Creation_User = Column(String(255), nullable=False)
    Name = Column(String(30), nullable=False)
    Description = Column(String(255), nullable=False)
    Created_DateTime = Column(DateTime(), nullable=False)
    Event_DateTime = Column(DateTime(), nullable=False)
    Location_Longitude = Column(DECIMAL(precision=9), nullable=False)
    Location_Latitude = Column(DECIMAL(precision=9), nullable=False)
    Users = relationship("EventUsers")
    __table_args__ = (
        ForeignKeyConstraint(["Creation_User"], ["users.User_ID"]),
    )

class EventUsers(Base):
    __tablename__ = "eventusers"
    Event_ID = Column(String(255), nullable=False, primary_key=True)
    User_ID = Column(String(255), nullable=False, primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint(["Event_ID"], ["events.Event_ID"]),
        ForeignKeyConstraint(["User_ID"], ["users.User_ID"]),
    )


