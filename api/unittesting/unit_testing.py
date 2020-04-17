import unittest
import requests
from jwt import decode
from pem import parse_file
from time import sleep
from os import getcwd
from os.path import join, dirname
from faker import Faker

p_key = str(
    parse_file("C:\\Users\\cerle\\Google Drive\\_ University Work\\Group Software Engineering\\Project\\unify-api\\privkey.pem")[0]
)

test_url="http://DESKTOP-JITKUGS:8000"

routes = {
    'create_user':  '/user/create',
    'user':         '/user/{User_ID}',
    'images': '/images',
}

content_types = {
    'json': 'application/json',
    'png':  'image/png',
    'jpg':  'image/jpeg'
}

image_dir = join(join(getcwd(), dirname(__file__)), 'images')

data_gen = Faker(['en_GB'])

def get_user_info():
    name = data_gen.name().split()
    First_Name, Last_Name = name if len(name) == 2 else name[1:3]
    Email = '{l_name}.{f_letter}@university.ac.uk'.format(l_name=Last_Name.lower(), f_letter=First_Name[0].lower())
    DateOfBirth = str(data_gen.date_of_birth(minimum_age=18, maximum_age=21))
    Password = data_gen.password()
    return {
        'Email':Email,
        'Password':Password,
        'First_Name':First_Name,
        'Last_Name':Last_Name,
        'DateOfBirth':DateOfBirth,
    }

def create_test_user():
    req = requests.post(test_url + routes['create_user'], json=get_user_info())
    data = req.json()['data']
    token = req.json()['access_token']
    try:
        yield req, data, token
    finally:
        req = requests.delete(
            test_url + routes['user'].format(User_ID=data['User_ID']), 
            headers=get_request_headers(token, content_types['json'])
        )

def get_request_headers(token, content_type):
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
        
        gen = create_test_user()
        req, data, token = next(gen)

        self.assertEqual(req.status_code, 201)
        self.assertIsNotNone(data)
        self.assertIsNotNone(token)
    
    def test_post_image_jpg(self):

        gen = create_test_user()
        req, data, token = next(gen)
        
        with open(join(image_dir, 'test.jpg'), 'rb') as image:
            post_req = requests.post(
                test_url + routes['images'],
                data=image,
                headers = get_request_headers(token, content_types['jpg'])
            )

        self.assertEqual(post_req.status_code, 201)

        del_req = requests.delete(
            test_url + routes['images'] + "?User_ID={User_ID}&Picture_Path={Picture_Path}".format(
                User_ID=data['User_ID'],
                Picture_Path=post_req.json()['data']['image']
            ),
            headers = get_request_headers(token, content_types['json'])
        )

        self.assertEqual(del_req.status_code, 200)


if __name__ == "__main__":
    unittest.main()