from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User, Category

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Create User')
    
    def __init__(self, original_user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (self.original_user is None or user.id != self.original_user.id):
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (self.original_user is None or user.id != self.original_user.id):
            raise ValidationError('Please use a different email address.')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat New Password', 
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Category')

class BookForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired(), Length(min=1, max=200)])
    author = StringField('Author Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    file = FileField('Book File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'epub', 'mobi', 'txt', 'doc', 'docx'], 
                   'Only PDF, EPUB, MOBI, TXT, DOC, and DOCX files are allowed!')
    ])
    submit = SubmitField('Upload Book')
    
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

class EditBookForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired(), Length(min=1, max=200)])
    author = StringField('Author Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Book')
    
    def __init__(self, *args, **kwargs):
        super(EditBookForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

class SearchForm(FlaskForm):
    query = StringField('Search books by title or author...', validators=[DataRequired()])
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.category.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
