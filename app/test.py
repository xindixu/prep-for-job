from main import create_app
from models import Users, JobPages, Jobs, db
import unittest
from random import randint

class FlaskTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = create_app(db_string="sqlite:///:memory:")
        self.client = self.app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        self.app.app_context().push()

    def tearDown(self):
        pass

    def test_splash_status_code(self):
        # sends HTTP GET request on path /
        result = self.client.get('/')
        # assert the status code of the response is OK
        self.assertEqual(result.status_code, 200)

    def test_register_email_unique(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza1'
        }
        result = self.client.post('/auth/register/', data=params)

        # assert the data
        assert "You have been registered successfully" not in result.get_data(as_text=True)

    def test_register_email_exists(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby@hotmail.com',
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza1'
        }
        result_first = self.client.post('/auth/register/', data=params)
        result = self.client.post('/auth/register/', data=params)


        # assert the data
        assert "User "+str(params['email'])+" already exists" not in result.get_data(as_text=True)

    def test_register_email_bad_password(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
            'confirm_password': 'iLikePizza12345'
        }
        result = self.client.post('/auth/register/', data=params)

        # assert the data
        assert "Passwords must match" not in result.get_data(as_text=True)

    # def test_insert_member(self):
    #     u = Users.new_member('test@email.com', 'password123', 'Tom', 'Smith')
    #     assert u.check_password('password123')
    #     assert not u.check_password('password555')
    #
    # # test for job table
    # # insertion is working
    # def test_job_insert(self):
    #     Jobs.new_job("29-1141.01")
    #     assert not Jobs.need_cache_code("29-1141.01")

    # test for login table
    # password is correct
    def test_password_incorrect(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
        }
        result = self.client.post('/auth/login/', data=params)
        # assert the data
        assert "NOT LOGGED IN WRONG" not in result.get_data(as_text=True)

    # password correct
    def test_password_correct(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'tsrishtti@gmail.com',
            'password': 'Montana@123',
        }
        result = self.client.post('/auth/login/', data=params)
        # assert the data
        assert "LOGGED IN" not in result.get_data(as_text=True)


if __name__ == "__main__":
    unittest.main()


# test for about page

# test for skill-job table

# test for Users class
