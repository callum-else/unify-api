import unittest
import requests
from jwt import decode
from pem import parse_file
from time import sleep

p_key = str(
    parse_file("C:\\Users\\cerle\\Google Drive\\_ University Work\\Group Software Engineering\\Project\\unify-api\\privkey.pem")[0]
)

test_url="http://DESKTOP-JITKUGS:8000"

routes = {
    'create_user':  '/user/create',
    'user':         '/user/{User_ID}'
}

content_types = {
    'json': 'application/json',
    'png':  'image/png',
    'jpg':  'image/jpeg'
}

user_info = {
    'Email':'unittest_email@email.ac.uk',
    'Password':'unittest_password',
    'First_Name':'unittest_first_name',
    'Last_Name':'unittest_last_name',
    'DateOfBirth':'2020-01-01',
}

def create_test_user(self):
    req = requests.post(test_url + routes['create_user'], json=user_info)
    data = req.json()['data']
    token = decode(req.json()['access_token'],p_key,algorithms='HS256')
    try:
        yield req, data, token
    finally:
        req = requests.delete(
            test_url + routes[1].format(User_ID=data['User_ID']), 
            headers=get_request_headers(token, content_types['json'])
        )

def get_request_headers(self, token, content_type):
    return {
        'Authorization':'jwt {token}'.format(token=token),
        'Content-Type':content_type
    }

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

class TestUserConnections(unittest.TestCase):

    def test_user_post(self):
        
        req, data, token = create_test_user()

        self.assertEqual




if __name__ == "__main__":
    unittest.main()