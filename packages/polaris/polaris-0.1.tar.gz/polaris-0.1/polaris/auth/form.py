from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()


class SignupForm(Form):
    email = TextField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class LoginForm(Form):
    email = TextField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
