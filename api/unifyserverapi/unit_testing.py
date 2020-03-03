import unittest
import requests

class TestUserConnections(unittest.TestCase):

    def test_user_post(self):
        user = {
            'Email':'unittest_email@email.com',
            'Password':'unittest_password',
            'First_Name':'unittest_first_name',
            'Last_Name':'unittest_last_name',
            'DateOfBirth':'2020-01-01',
            'User_Created':'2020-01-01T00:00:00Z',
            'Last_Login':'2020-01-01T00:00:00Z'
        }

        request = requests.post(url="localhost:8000/user/create/unittest_user_id", params=user)
        data = request.json()['results'][0]

        self.assertEqual(data['User_ID'], 'unittest_user_id')
        self.assertEqual(data['Email'], user['Email'])
        self.assertEqual(data['Password'], user['Password'])
        self.assertEqual(data['First_Name'], user['First_Name']) 
        self.assertEqual(data['Last_Name'], user['Last_Name'])

if __name__ == "__main__":
    unittest.main()