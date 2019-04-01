from main import create_app
import unittest
from random import randint

class FlaskBookshelfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = create_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_splash_status_code(self):
        # sends HTTP GET request on path /
        result = self.app.get('/')

        # assert the status code of the response is OK
        self.assertEqual(result.status_code, 200)

    def test_splash_data(self):
        # sends HTTP GET request on path /
        result = self.app.get('/')

        # assert the data
        self.assertEqual(result.data, "This will fail!")

    def test_register_email_unique(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza1'
        }
        result = self.app.post('/auth/register/', data=params)

        # assert the data
        self.assertEqual(result.data, "You have been registered successfully")

    def test_register_email_exists(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby@hotmail.com',
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza1'
        }
        result_first = self.app.post('/auth/register/', data=params)
        result = self.app.post('/auth/register/', data=params)


        # assert the data
        self.assertEqual(result.data, "User "+str(params['email'])+" already exists")

    def test_register_email_bad_password(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza12345'
        }
        result = self.app.post('/auth/register/', data=params)

        # assert the data
        self.assertEqual(result.data, "Passwords must match")



# test for job table
# description is not null
# Salary is not null
# job is unique

# test for skill table
# description is not null
# skill is unique
# title is not null

# test for skill-job table
# unique skill-job

# test for register table
# email unique
# email is an email (must have @ and .)
# password is same with retype
# cannot be blank

# test for login table
# password is correct
# password cannot be blank
# retrieve password is working
