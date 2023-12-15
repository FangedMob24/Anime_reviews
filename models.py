from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Review(db.Model):
    """For rating and commenting on a specific show by a user"""
    
    __tablename__ = 'reviews'
    
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    anime_id = db.Column(
        db.Integer,
        nullable=False
    )
    rating = db.Column(
        db.Integer,
        nullable=False
    )
    comment = db.Column(
        db.Text
    )
    username = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='cascade'),
        nullable=False
    )
    users = db.relationship(
        'User', backref = 'reviews'
    )

    @classmethod
    def reviewing(cls, username, comment, rating, anime_id):
        review = Review(
            username=username,
            anime_id=anime_id,
            rating=rating,
            comment=comment or ''
        )
        print(review)

        db.session.add(review)
        return review


class User(db.Model):
    """User information"""

    __tablename__ = 'users'

    username = db.Column(
        db.Text,
        primary_key=True,
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    liked_genres = db.Column(
        db.Text,
        nullable=False
    )

    liked_va = db.Column(
        db.Text
    )

    bookmarks = db.Column(
        db.Text
    )

    def __repr__(self):
        return f"<User #{self.username}: {self.first_name}, {self.last_name}>"
    
    def fav_genre_list(self):
        """gets the genres liked and returns as a list"""
        genre_str = self.liked_genres.rsplit(", ")

        return [int(x) for x in genre_str]
    
    def fav_vc_list(self):
        """gets the Voice Actors liked and returns as a list"""
        if self.liked_va:
            return self.liked_va.rsplit(", ")
        
        return []
    
    def bookmark_anime_list(self):
        """gets the bookmarked anime and returns as a list"""
        if self.bookmarks:
            return self.bookmarks.rsplit(", ")
        
        return []
    
    @classmethod
    def sign(cls, username, email, first_name, last_name, password, liked_genres):
        """
        Sign up a user with hashed password and selected genres
        """

        joined = ", ".join(liked_genres)

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_pwd,
            liked_genres=joined
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """ To authenticate that the password and user match"""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False
    
    @classmethod
    def edit(cls, orig_username, new_username, email, first_name, last_name):
        user = cls.query.filter_by(username=orig_username).first()

        user.username = new_username or user.username
        user.email = email or user.email
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name

        return user

    @classmethod
    def bookmark_it(cls, username, bookmarks):
        user = cls.query.filter_by(username=username).first()

        joined = ", ".join(bookmarks)

        user.bookmarks = joined

        return user

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)