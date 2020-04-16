import requests

from jwt import decode
from json import dumps

from random import randint
from faker import Faker

from os import getcwd
from os.path import dirname, join

data_gen = Faker(['en_GB'])

test_url="http://DESKTOP-JITKUGS:8000"

routes = {
    'create_user':  '/user/create',
    'add_friend':   '/user/{User_ID}/friends/requests',
    'create_event': '/event/create',
    'attend_event': '/event/{Event_ID}/users',
}

content_types = {
    'json': 'application/json',
    'png':  'image/png',
    'jpg':  'image/jpeg'
}

def get_request_headers(token, content_type):
    return {
        'Authorization':'jwt {token}'.format(token=token),
        'Content-Type':content_type
    }

created_users = []
created_events = []

def create_test_user():
    name = data_gen.name().split()
    First_Name, Last_Name = name if len(name) == 2 else name[1:3]
    Email = '{l_name}.{f_letter}@university.ac.uk'.format(l_name=Last_Name.lower(), f_letter=First_Name[0].lower())
    DateOfBirth = str(data_gen.date_of_birth(minimum_age=18, maximum_age=21))
    Password = data_gen.password()
    user_info = {
        'Email':Email,
        'Password':Password,
        'First_Name':First_Name,
        'Last_Name':Last_Name,
        'DateOfBirth':DateOfBirth,
    }
    req = requests.post(test_url + routes['create_user'], json=user_info)
    if req.status_code >= 200 and req.status_code <= 203:
        created_users.append({
            'User_ID':req.json()['data']['User_ID'],
            'Email':Email,
            'Password':Password,
            'Auth_Token':req.json()['access_token'],
            'Friends':[]
        })
        print(
            'User Created: UID-{user}, {f_name} {l_name}.'.format(
                user=req.json()['data']['User_ID'],
                f_name=First_Name,
                l_name=Last_Name
            )
        )
    else:
        print(
            'Failed to create user: UID-{user}, {msg}.'.format(
                user=req.json()['data']['User_ID'],
                msg=req.reason
            )
        )
    req.close()

def create_test_event():
    Name = data_gen.sentence(4)
    Description = data_gen.sentence(12)
    DateTime = data_gen.date_time_between(start_date='-1y')
    Location = data_gen.address()
    event_info = {
        'Name':Name,
        'Description':Description,
        'DateTime':DateTime.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'Location':Location,
    }
    req = requests.post(
        test_url + routes['create_event'],
        json = event_info,
        headers = get_request_headers(
            created_users[randint(0,len(created_users)-1)]['Auth_Token'],
            content_types['json']
        ) 
    )
    if req.status_code >= 200 and req.status_code <= 203:
        created_events.append({
            'Event_ID':req.json()['data']['Event_ID'],
            'User_ID':req.json()['data']['User_ID'],
            'Users':[]
        })
        print(
            'Event Created: EID-{event} created by UID-{user}.'.format(
                event=req.json()['data']['Event_ID'],
                user=req.json()['data']['User_ID']
            )
        )
    else:
        print(
            'Failed to create event: EID-{event}, {msg}.'.format(
                event=req.json()['data']['Event_ID'],
                msg=req.reason
            )
        )
    req.close()
    
def create_friendship():
    Sender_Index = randint(0,len(created_users)-1)
    Reciever_Index = randint(0,len(created_users)-1)
    
    req = requests.post(
        test_url + routes['add_friend'].format(User_ID=created_users[Reciever_Index]['User_ID']),
        json={},
        headers=get_request_headers(
            created_users[Sender_Index]['Auth_Token'],
            content_types['json']
        )
    )
    if req.status_code >= 200 and req.status_code <= 203:
        resp = requests.patch(
            test_url + routes['add_friend'].format(User_ID=created_users[Sender_Index]['User_ID']),
            json={},
            headers=get_request_headers(
                created_users[Reciever_Index]['Auth_Token'],
                content_types['json']
            )
        )
        if resp.status_code >= 200 and req.status_code <= 203:
            created_users[Sender_Index]['Friends'].append(created_users[Reciever_Index]['User_ID'])
            created_users[Reciever_Index]['Friends'].append(created_users[Sender_Index]['User_ID'])
            print(
                'Friendship Created: UID-{sender} and UID-{reciever}.'.format(
                    sender=created_users[Sender_Index]['User_ID'],
                    reciever=created_users[Reciever_Index]['User_ID']
                )
            )
        else:
            print(
                'Failed to accept request: UID-{reciever} and UID-{sender}, {msg}.'.format(
                    reciever=created_users[Reciever_Index]['User_ID'],
                    sender=created_users[Sender_Index]['User_ID'],
                    msg=req.reason
                )
            )
        resp.close()
    else:
        print(
            'Failed to send friend request: UID-{sender} and UID-{reciever}, {msg}.'.format(
                reciever=created_users[Reciever_Index]['User_ID'],
                sender=created_users[Sender_Index]['User_ID'],
                msg=req.reason
            )
        )
    req.close()

def create_user_attendence():
    User_Index = randint(0,len(created_users)-1)
    Event_Index = randint(0,len(created_events)-1)

    req = requests.post(
        test_url + routes['attend_event'].format(Event_ID=created_events[Event_Index]['Event_ID']),
        json={},
        headers=get_request_headers(
            created_users[User_Index]['Auth_Token'],
            content_types['json']
        )
    )
    if req.status_code >= 200 and req.status_code <= 203:
        created_events[Event_Index]['Users'].append(User_Index)
        print(
            'User Attendance Created: UID-{user} attending EID-{event}.'.format(
                user=created_users[User_Index]['User_ID'],
                event=created_events[Event_Index]['Event_ID']
            )
        )
    else:
        print(
            'Failed to request attendence: UID-{user} attending EID-{event}, {msg}.'.format(
                user=created_users[User_Index]['User_ID'],
                event=created_events[Event_Index]['Event_ID'],
                msg=req.reason
            )
        )
    req.close()

def generate_data(user_num=30, event_num=25, relationship_modifier=3):
    for i in range(user_num):
        create_test_user()
    
    for i in range(user_num * relationship_modifier):
        create_friendship()

    for i in range(event_num):
        create_test_event()

    for i in range(user_num * relationship_modifier):
        create_user_attendence()

    file_path = join(join(getcwd(), dirname(__file__)), 'generated_data.json')
    with open(file_path, 'w+') as output:
        output_data = {'Users':created_users, 'Events':created_events}
        output.write(dumps(output_data, sort_keys=True, indent=4, separators=(',', ': ')))
        print('Output document created successfully.')
        output.close()

generate_data(user_num=40, event_num=25)