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
        self.app = create_app().test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_splash_status_code(self):
        # sends HTTP GET request on path /
        result = self.app.get('/')
        # assert the status code of the response is OK
        self.assertEqual(result.status_code, 200)
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
    # insertion is working
    def test_job_insert(self):
        s = Jobs(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'job', salary = 0, description = 'this is a job',parent_skill = "none")
        db.session.add(s)
        db.session.commit()


        r = db.session.query(Jobs).filter_by(id = '9999').one()
        self.assertEqual(str(r.id), '9999')

        db.session.query(Jobs).filter_by(id = '9999').delete()
        db.session.commit()

    # description is not null
    def test_job_description(self):
        error = False
        s = Jobs(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'job', salary = 0, description = '',parent_skill = "none")
        try:
            db.session.add(s)
            db.session.commit()
        except:
            error = True

        self.assertEqual(error, True)

        try:
            db.session.query(Jobs).filter_by(id = '9999').delete()
            db.session.commit()
        except:
            pass

    # Salary is nullable
    def test_job_salary(self):
        error = False
        s = Jobs(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'job', description = 'this is a job',parent_skill = "none")
        try:
            db.session.add(s)
            db.session.commit()
        except:
            error = True

        self.assertEqual(error, False)

        db.session.query(Jobs).filter_by(id = '9999').delete()
        db.session.commit()

    # test for skill table
    # insertion is working
    def test_skill_insert(self):
        s = Skills(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'skill', importance = 0, description = 'this is a skill',parent_skill = "none")
        db.session.add(s)
        db.session.commit()


        r = db.session.query(Skills).filter_by(id = '9999').one()
        self.assertEqual(str(r.id), '9999')

        db.session.query(Jobs).filter_by(id = '9999').delete()
        db.session.commit()
    # description is nullable
    def test_skill_description(self):
        error = False
        s = Skills(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'skill', importance = 0, description = '',parent_skill = "none")

        try:
            db.session.add(s)
            db.session.commit()
        except:
            error = True
        self.assertEqual(error, False)

        try:
            db.session.query(Skills).filter_by(id = '9999').delete()
            db.session.commit()
        except:
            pass
    # parent_skill is nullable
    def test_skill_description(self):
        error = False
        s = Skills(id='9999', created_at ='1999-01-08', updated_at = '1999-10-08',title = 'skill', importance = 0, description = 'this is a skill',parent_skill = "")

        try:
            db.session.add(s)
            db.session.commit()
        except:
            error = True
        self.assertEqual(error, False)

        try:
            db.session.query(Skills).filter_by(id = '9999').delete()
            db.session.commit()
        except:
            pass



    # test for login table
    # password is correct
    def test_password_incorrect(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'bobby_'+str(str(randint(1000,99999))+'@hotmail.com'),
            'password': 'iLikePizza1',
        }
        result = self.app.post('/auth/login/', data=params)

        # assert the data
        self.assertEqual(result.data, "NOT LOGGED IN WRONG")

    # password correct
    def test_password_correct(self):
        # sends HTTP GET request on path /
        params = {
            'email': 'tsrishtti@gmail.com',
            'password': 'Montana@123',
        }
        result = self.app.post('/auth/login/', data=params)

        # assert the data
        self.assertEqual(result.data, "LOGGED IN")

    # logout
    def test_log_out(self):
        # sends HTTP GET request on path /

        result = self.app.post('/auth/logout/', data=params)

        # assert the data
        self.assertEqual(result.data, "LOGGED OUT")

unittest.main()


# test for about page

# test for skill-job table

# test for Users class
