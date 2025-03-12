from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), Regexp('^[A-Za-z]+$', message="First name can only contain letters.")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), Regexp('^[A-Za-z]+$', message="Last name can only contain letters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8, message="Password must be at least 8 characters long."),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', message="Password must contain at least one uppercase letter, one lowercase letter, and one number.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message="Passwords didn't match.")
    ])
    role = SelectField('Role', choices=[('student', 'Student'), ('professor', 'Professor')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address.")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
