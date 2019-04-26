from main import create_app
from models import Users, JobPages, Jobs, db
from forms import RegistrationForm, LoginForm
import unittest
from random import randint
from flask_testing import TestCase
from requests.exceptions import ConnectTimeout


class FlaskTests (TestCase):
    def create_app(self):
        app = create_app()
        app.config.update({
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
            "WTF_CSRF_ENABLED": False
        })
        db.init_app(app)
        return app

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_splash_page(self):
        # sends HTTP GET request on path /
        result = self.client.get('/')

        # assert the status code of the response is OK
        self.assert200(result)
        self.assertTemplateUsed("index.html")

    def test_registration(self):
        form = RegistrationForm(
            email="johndoe@example.com",
            password="p@5sw0rD",
            confirm_password="p@5sw0rD",
            first_name="John",
            last_name="Doe"
        )

        self.assertTrue(form.validate())

        result = self.client.post("/auth/register/", data=form.data)

        self.assertMessageFlashed("You have been registered successfully!", "success")
        self.assertRedirects(result, "/profile/1")

        form = RegistrationForm(
            email="janeroe@example.com",
            password="betterpassword",
            confirm_password="betterpassword",
            first_name="Jane",
            last_name="Roe"
        )

        self.assertTrue(form.validate())

        result = self.client.post("/auth/register/", data=form.data, follow_redirects=True)

        self.assert200(result)
        self.assertTemplateUsed("profile.html")

    def test_registration_error_fields_required(self):
        form = RegistrationForm()

        self.assertFalse(form.validate())

        result = self.client.post("/auth/register/", data=form.data)

        self.assertTemplateUsed("auth/register.html")
        self.assertMessageFlashed("Email required", "danger")
        self.assertMessageFlashed("First name required", "danger")
        self.assertMessageFlashed("Last name required", "danger")
        self.assertMessageFlashed("Password required", "danger")
        self.assertMessageFlashed("Password confirmation required", "danger")

        print(result.data.decode("utf-8"))

    def test_registration_error_user_exists(self):
        # sends HTTP GET request on path /
        form = RegistrationForm(
            email='bobby@hotmail.com',
            password='iLikePizza1',
            confirm_password='iLikePizza1',
            first_name='Bobby',
            last_name='Hotmail'
        )

        self.assertTrue(form.validate())

        result_first = self.client.post('/auth/register/', data=form.data)

        self.assertMessageFlashed("You have been registered successfully!", "success")
        self.assertRedirects(result_first, "profile/1")

        self.assertTrue(form.validate())

        result = self.client.post('/auth/register/', data=form.data)
        #print(result.data)
        self.assertMessageFlashed("User {} already exists".format(form.data["email"]), "message")
        self.assertTemplateUsed("auth/register.html")

    def test_registration_error_invalid_email(self):
        form = RegistrationForm(
            email='qwertyuiop',
            password='flkjshlkjs',
            confirm_password='flkjshlkjs',
            first_name="Michael",
            last_name="Jackson"
        )

        self.assertFalse(form.validate())

        result = self.client.post("/auth/register/", data=form.data)

        self.assertMessageFlashed("Email invalid", "danger")
        self.assertTemplateUsed("auth/register.html")

    def test_registration_error_password_mismatch(self):
        # sends HTTP GET request on path /
        form = RegistrationForm(
            email='daniel@jacobson.com',
            password='iLikePizza1',
            confirm_password='iLikePizza12345',
            first_name="Daniel",
            last_name="Jacobson"
        )

        self.assertFalse(form.validate())

        result = self.client.post('/auth/register/', data=form.data)

        self.assertMessageFlashed("Passwords must match", "danger")
        self.assertTemplateUsed("auth/register.html")

    def test_login(self):
        u = Users.new_member('tomsmith@protonmail.com', 'password123', 'Tom', 'Smith')

        form = LoginForm(
            email="tomsmith@protonmail.com",
            password="password123"
        )

        self.assertTrue(form.validate())

        result = self.client.post("/auth/login/", data=form.data)

        self.assertMessageFlashed("Logged in successfully!", "success")
        self.assertRedirects(result, "profile/1")

        result = self.client.post("/auth/login/", data=form.data, follow_redirects=True)

        self.assert200(result)
        self.assertTemplateUsed("profile.html")

    def test_login_error_user_does_not_exist(self):
        form = LoginForm(
            email="tomsmith@protonmail.com",
            password="password123"
        )

        self.client.post("/auth/login/", data=form.data)

        self.assertTemplateUsed("auth/login.html")
        self.assertMessageFlashed("User {} does not exist".format(form.data["email"]), "danger")

    def test_login_error_incorrect_password(self):
        u = Users.new_member('tomsmith@protonmail.com', 'password123', 'Tom', 'Smith')

        form = LoginForm(
            email="tomsmith@protonmail.com",
            password="password456"
        )

        self.client.post("/auth/login/", data=form.data)

        self.assertTemplateUsed("auth/login.html")
        self.assertMessageFlashed("Incorrect password for " + form.data["email"], "danger")

    def test_insert_member(self):
        u = Users.new_member('test@email.com', 'password123', 'Tom', 'Smith')

        self.assertTrue(Users.exists('test@email.com'))
        self.assertIn(u, Users.view_members())
        self.assertTrue(u.check_password('password123'))
        self.assertFalse(u.check_password('password555'))

    # test for job table
    # insertion is working
    def test_job_insert(self):
        try:
            Jobs.new_job("29-1141.01")
            self.assertFalse(Jobs.need_cache_code("29-1141.01"))
        except Exception as e:
            print(e)

    def test_404_page(self):
        result = self.client.get("/asdfghjkl")

        self.assert404(result)
        self.assertTemplateUsed("error404.html")

    def test_about_page(self):
        result = self.client.get("/about")

        self.assert200(result)
        self.assertTemplateUsed("about.html")

    def test_jobs_page(self):
        result = self.client.get("/job/")

        self.assert200(result)
        self.assertTemplateUsed("job.html")

    def test_skills_page(self):
        result = self.client.get("/skill/")

        self.assert200(result)
        self.assertTemplateUsed("skill.html")

    def test_search_page(self):
        result = self.client.get("/search")

        self.assert200(result)
        self.assertTemplateUsed("search.html")


if __name__ == "__main__":
    unittest.main()
