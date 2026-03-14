from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DateTimeField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from datetime import datetime

class LoginForm(FlaskForm):
    """Login form for users"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Registration form for new users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(max=20)])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Electronics', 'Electronics'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
        ('Electrical', 'Electrical')
    ], validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    batch = StringField('Batch', validators=[Optional(), Length(max=10)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Register')

class ProfileUpdateForm(FlaskForm):
    """Form for updating user profile"""
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', 
                                       validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')

class NoticeForm(FlaskForm):
    """Form for creating/editing notices"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Academic', 'Academic'),
        ('Event', 'Event'),
        ('Holiday', 'Holiday'),
        ('Exam', 'Exam'),
        ('Result', 'Result'),
        ('Important', 'Important'),
        ('General', 'General')
    ], validators=[DataRequired()])
    
    # Fixed: RadioField is now properly imported
    priority = RadioField('Priority', choices=[
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()], default='normal')
    
    is_featured = BooleanField('Featured Notice')
    banner_image = FileField('Banner Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    attachment = FileField('Attachment', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Documents only!')
    ])
    
    start_date = DateTimeField('Start Date', format='%Y-%m-%dT%H:%M', 
                              validators=[DataRequired()], 
                              default=datetime.now)
    expiry_date = DateTimeField('Expiry Date', format='%Y-%m-%dT%H:%M', 
                               validators=[DataRequired()])
    
    submit = SubmitField('Post Notice')

class ContactForm(FlaskForm):
    """Form for contact messages"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')