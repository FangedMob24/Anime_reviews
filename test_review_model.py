import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Review

os.environ['DATABASE_URL'] = "postgresql:///anime_review_test"

from app import app

db.drop_all()
db.create_all()

class ReviewModelTestCase(TestCase):
    """Test review model"""