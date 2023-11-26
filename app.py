import os

from flask import Flask, render_template, request, redirect, session, g
from sqlalchemy.exc import IntegrityError
import requests

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