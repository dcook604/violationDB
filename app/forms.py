from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
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
