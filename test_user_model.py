import os
from unittest import TestCase
from sqlalchemy import exc

from flask import Flask
from models import db, User, Review

os.environ['DATABASE_URL'] = "postgresql:///anime_review_test"

from app import app

with app.app_context():
    db.drop_all()
    db.create_all()

USER_DATA = {
    "username" : "sampleuser",
    "password" : "HASHED_PASSWORD",
    "email" : "sample@sample.com",
    "first_name" : "John",
    "last_name" : "Doe",
    "liked_genres" : "Action"
}

class UserModelTestCase(TestCase):
    """Test user model"""

    def setUp(self):
        """Create test client, add smaple data"""
        User.query.delete()
        Review.query.delete()

        sample = User(**USER_DATA)
        db.session.add(sample)
        db.session.commit()

        db.session.refresh(sample)

        self.sample = sample

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User.sign(
                username= "tester",
                password= "HASHED_PASSWORD",
                email= "test@test.com",
                first_name= "test",
                last_name= "form",
                liked_genres= "action"
        )

        db.session.add(u)
        db.session.commit()
        with app.app_context():
            self.assertEqual(User.query.get_or_404("tester"), "tester")