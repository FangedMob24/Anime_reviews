import os

from flask import Flask, render_template, request, redirect, session, g, flash
from sqlalchemy.exc import IntegrityError
import requests
from forms import NewUserForm, LoginForm

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
                liked_genres='/'.join(form.liked_genres.data)
            )
            db.session.commit()

        except IntegrityError:
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
# General routes

@app.route('/anime/<int:anime_id>')
def anime_pg(anime_id):
    """brings up the specific anime"""
    anime = requests.get(f'https://api.jikan.moe/v4/anime/{anime_id}')

    return render_template('anime/anime.html', anime=anime.json())

@app.route('/anime/search')
def anime_query():
    search = request.args.get('q')
    page = request.args.get('page') or 1

    p = {'q':search, 'page':page}

    animes = requests.get('https://api.jikan.moe/v4/anime',params=p)
    
    return render_template('anime/search.html',animes=animes.json(),search=search)

#######################
# Home page

@app.route('/home')
def home_page():
    """home page of the site"""
    anime = requests.get('https://api.jikan.moe/v4/anime')
    return render_template('home.html', anime=anime.json())

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