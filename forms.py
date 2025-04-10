from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, FloatField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from models import User, RegistrationToken
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('community', 'Community Member')
    ], validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

class SpeciesForm(FlaskForm):
    name = StringField('Species Name', validators=[DataRequired()])
    scientific_name = StringField('Scientific Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    population = StringField('Population Estimate')
    conservation_status = SelectField('Conservation Status', choices=[
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EW', 'Extinct in the Wild'),
        ('EX', 'Extinct')
    ])
    habitat = StringField('Habitat')
    threats = TextAreaField('Threats')

class LibraryResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    resource_type = SelectField('Type', choices=[
        ('article', 'Article'),
        ('guide', 'Guide'),
        ('research', 'Research')
    ], validators=[DataRequired()])
    is_public = SelectField('Visibility', choices=[
        ('True', 'Public'),
        ('False', 'Private')
    ], validators=[DataRequired()])

class ThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])

class SightingForm(FlaskForm):
    species_id = SelectField('Species', coerce=int, validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    sighting_date = DateField('Date of Sighting', validators=[DataRequired()],
        default=datetime.today)
    photos = FileField('Upload Photos', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=2, max=500, message='Comment must be between 2 and 500 characters')
    ])

class ProgramForm(FlaskForm):
    title = StringField('Program Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    start_date = DateField('Start Date', validators=[DataRequired()], default=datetime.today)
    end_date = DateField('End Date', validators=[DataRequired()], default=datetime.today)

class GenerateTokenForm(FlaskForm):
    """Form for teachers to generate registration tokens"""
    notes = TextAreaField('Notes (optional)', description='Any notes about this registration token')

class StudentRegistrationForm(FlaskForm):
    """Form for student registration with token validation"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    registration_token = StringField('Registration Token', validators=[
        DataRequired(),
        Length(min=36, max=36, message="Invalid token format")
    ])
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
            
    def validate_registration_token(self, field):
        valid, message = RegistrationToken.validate_token(field.data)
        if not valid:
            raise ValidationError(message)