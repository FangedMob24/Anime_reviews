from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange
import requests

def getList():
    genres = requests.get('https://api.jikan.moe/v4/genres/anime')
    genre_list = [(str(x['mal_id']),x['name']) for x in genres.json()['data']]
    return genre_list

class NewUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[Length(min=6)])

    email = StringField('E-mail', validators=[DataRequired(), Email()])

    first_name = StringField('First Name', validators=[DataRequired()])

    last_name = StringField('Last Name', validators=[DataRequired()])

    liked_genres = SelectMultipleField('Genre', choices=getList(), validate_choice=False, validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Form for logging in"""

    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[Length(min=6)])

class ReviewForm(FlaskForm):
    """Form for Reviewing Anime"""

    rate = IntegerField('Stars', validators=[DataRequired(),NumberRange(min=1,max=10)])
    
    comment = StringField('Comments', validators=[Length(max=200)])