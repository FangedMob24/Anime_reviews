import os

from flask import Flask, render_template, request, redirect, session, g, flash
from sqlalchemy.exc import IntegrityError
import requests
from forms import NewUserForm, LoginForm, ReviewForm

from models import db, connect_db, User, Review

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///anime_review_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)

@app.route('/')
def default():
    """redirects to home page"""
    return redirect("/home")

#######################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global"""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """log in user"""
    session[CURR_USER_KEY] = user.username

def do_logout():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/account/signup', methods=['GET','POST'])
def user_signup():
    """gets a form to sign up user"""

    form = NewUserForm()

    if form.validate_on_submit():
        try:
            user = User.sign(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                liked_genres=form.liked_genres.data
            )
            db.session.commit()
        except IntegrityError:
            print("work")
            return render_template('account/signup.html',form=form)
        
        do_login(user)
        
        return redirect('/')
        
    else:
        return render_template('account/signup.html', form=form)
    
@app.route('/account/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('account/login.html', form=form)
    
@app.route('/account/logout')
def logout():
    """Handle logout of user"""
    do_logout()
    flash("successful logout")
    return redirect("/account/login")

#######################
# Account routes

@app.route('/account/<username>')
def profile(username):
    """User page"""
    user = User.query.get_or_404(username)

    genres = requests.get('https://api.jikan.moe/v4/genres/anime')

    animes = []

    for bookmark in user.bookmark_anime_list():
        anime = requests.get(f'https://api.jikan.moe/v4/anime/{bookmark}')
        animes.append(anime.json())

    return render_template('account/profile.html',user=user, animes=animes, genres=genres.json())

#######################
# General routes

@app.route('/anime/<int:anime_id>')
def anime_pg(anime_id):
    """brings up the specific anime"""
    anime = requests.get(f'https://api.jikan.moe/v4/anime/{anime_id}')

    reviews = Review.query.filter(Review.anime_id == anime_id).all()

    return render_template('anime/anime.html', anime=anime.json(), reviews=reviews)

@app.route('/anime/search')
def anime_query():
    search = request.args.get('q')
    genre = request.args.get('genres')
    page = request.args.get('page') or 1

    p = {'page':page}

    if genre:
        print(genre)
        p['genres'] = int(genre)
    if search:
        p['q'] = search

    animes = requests.get('https://api.jikan.moe/v4/anime',params=p)
    
    return render_template('anime/search.html',animes=animes.json(),search=search)

@app.route('/anime/<int:anime_id>/bookmark', methods=["GET","POST"])
def bookmark(anime_id):
    """Bookmark fav anime"""
    bookmarks = g.user.bookmark_anime_list()
    
    if str(anime_id) in bookmarks:
        bookmarks.remove(str(anime_id))
        user = User.bookmark_it(g.user.username,bookmarks)
    else:
        bookmarks.append(str(anime_id))
        user = User.bookmark_it(g.user.username,bookmarks)
    
    db.session.commit()

    return redirect(f'/anime/{anime_id}')

#######################
# Review Routes

@app.route('/anime/<int:anime_id>/review', methods=["GET", "POST"])
def review(anime_id):
    """Handle user login."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    anime = requests.get(f'https://api.jikan.moe/v4/anime/{anime_id}')

    form = ReviewForm()

    if form.validate_on_submit():
        try:
            review = Review.reviewing(
                username=g.user.username,
                anime_id=anime_id,
                rating=form.rate.data,
                comment=form.comment.data,
            )
            db.session.commit()

        except IntegrityError:
            return render_template('anime/review.html',form=form, anime=anime.json())
        
        return redirect(f'/anime/{anime_id}')
    else:
        return render_template('anime/review.html', form=form, anime=anime.json())

#######################
# Home page

@app.route('/home')
def home_page():
    """home page of the site"""
    anime = requests.get('https://api.jikan.moe/v4/anime')
    
    if g.user:
        p = {'genres': g.user.fav_genre_list()}
        rec_anime = requests.get('https://api.jikan.moe/v4/anime',params=p)
        user_dict = rec_anime.json()
        user_dict['user'] = True
    else:
        user_dict = {'user': False}

    return render_template('home.html', anime=anime.json(), rec_anime=user_dict)

#######################
# Turn of caching in flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req