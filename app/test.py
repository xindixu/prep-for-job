from main import create_app
import unittest

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

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the response data
        self.assertEqual(result.data, "Hello World!!!")



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
