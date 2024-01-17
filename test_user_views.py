import os
from unittest import TestCase
from models import db, connect_db, User, Review

os.environ['DATABASE_URL'] = "postgresql:///anime_review_test"

from app import app, CURR_USER_KEY

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for Users and Reviews"""