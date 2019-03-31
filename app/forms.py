from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.csrf.core import CSRFTokenField


class RegistrationForm (FlaskForm):
    email = StringField(u"Email", validators=[validators.DataRequired(), validators.Email("Email invalid")])
    password = PasswordField(u"Password", validators=[
        validators.DataRequired(),
        validators.EqualTo("confirm_password", "Passwords must match"),
        validators.Length(6, 50)
    ])
    confirm_password = PasswordField(u"Retype Password", validators=[validators.DataRequired()])
    submit = SubmitField(u"Register")


class LoginForm (FlaskForm):
    email = StringField(u"Email", validators=[validators.DataRequired(), validators.Email("Email invalid")])
    password = PasswordField(u"Password", validators=[validators.DataRequired()])
    submit = SubmitField(u"Log In")



