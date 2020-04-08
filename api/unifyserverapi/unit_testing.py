import unittest
import requests
from jwt import decode
from pem import parse_file
from time import sleep

p_key = str(
    parse_file("C:\\Users\\cerle\\Google Drive\\_ University Work\\Group Software Engineering\\Project\\unify-api\\privkey.pem")[0]
)

test_url="http://DESKTOP-JITKUGS:8000"
routes = [
    "/user/create",
    "/user/{User_ID}"
]

class TestUserConnections(unittest.TestCase):

    auth_token = ""
    User_ID = 0

    def test_user_post(self):
        user = {
            'Email':'unittest_email@email.ac.uk',
            'Password':'unittest_password',
            'First_Name':'unittest_first_name',
            'Last_Name':'unittest_last_name',
            'DateOfBirth':'2020-01-01',
        }

        req = requests.post(test_url + routes[0], json=user)

        sleep(6)

        data = req.json()['data']
        payload = decode(req.json()['access_token'],p_key,algorithms='HS256')

        self.auth_token = req.json()['access_token']
        self.User_ID = data['User_ID']
        self.assertEqual(data['First_Name'], user['First_Name']) 
        self.assertEqual(data['Last_Name'], user['Last_Name'])
        self.assertEqual(payload['user']['User_ID'], data['User_ID'])

        tags = {
            "tags": [
                {
                    "User_ID":self.User_ID,
                    "User_Tag":"Test Tag 1"
                },
                {
                    "User_ID":self.User_ID,
                    "User_Tag":"Test Tag 2"
                }
            ]
        }

        req = requests.put(
            test_url + routes[1].format(User_ID=self.User_ID), 
            json=tags, 
            headers={
                "Authorization":("JWT " + self.auth_token),
                'Content-Type':'application/json'
            }
        )

        sleep(6)

        print(req.json())
        self.assertTrue(True)

        req = requests.delete(
            test_url + routes[1].format(User_ID=self.User_ID), 
            headers={
                "Authorization":("JWT " + self.auth_token),
                'Content-Type':'application/json'
            }
        )
        self.assertEqual(req.status_code, 200)


if __name__ == "__main__":
    unittest.main()