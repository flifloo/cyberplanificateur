from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
import trello, trello_credentials

class LoginForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

    def validate_username(self, username):
        if not User.query.filter_by(username = username.data).first():
            raise ValidationError("Invalid username.")

    def validate_password(self, password):
        user = User.query.filter_by(username = self.username.data).first()
        if user and not user.check_password(password.data):
            raise ValidationError("Invalid password.")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators = [DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

class TrelloAPIForm(FlaskForm):
    token = StringField("Token", validators = [DataRequired()])
    submit = SubmitField("Connect")

    def validate_token(self, token):
        try:
            trello.TrelloClient(api_key = trello_credentials.api_key, token = token.data).list_boards()
        except:
            raise ValidationError("Invalid Trello Token")
