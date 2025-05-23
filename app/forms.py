from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset Password')

class ViolationForm(FlaskForm):
    # Add all relevant fields
    category = SelectField('Category', choices=[('Noise', 'Noise'), ('Parking', 'Parking'), ('Garbage', 'Garbage'), ('Pets', 'Pets'), ('Other', 'Other')], validators=[DataRequired()])
    building = StringField('Building', validators=[DataRequired()])
    unit_number = StringField('Incident Units', validators=[DataRequired()])
    incident_area = StringField('Incident Area')
    report_to = StringField('Report To')
    concierge_shift = StringField('Concierge Shift')
    incident_date = StringField('Entry Date', validators=[DataRequired()])
    incident_time = StringField('Time')
    people_involved = StringField('People Involved')
    noticed_by = StringField('Noticed By')
    people_called = StringField('People Called')
    subject = StringField('Subject', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    initial_action = TextAreaField('Initial Action Taken')
    resolution = TextAreaField('Resolution')
    photos = FileField('Photos')
    pdfs = FileField('PDFs')
    submit = SubmitField('Submit Violation')

class UserCreateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('manager', 'Manager'), ('admin', 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Create User')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class UserEditForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('manager', 'Manager'), ('admin', 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    set_temporary_password = BooleanField('Set Temporary Password')
    submit = SubmitField('Update User')

class UserPasswordChangeForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
