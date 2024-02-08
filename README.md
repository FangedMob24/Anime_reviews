# anime-review-bookmark

https://anime-review-bookmark.onrender.com

A simple database-driven website for bookmarking and reviewing anime.

Api: https://docs.api.jikan.moe/
The API limits 25 shows per call so you have to make a workaround like making multiple calls.

Features:
The features that I have implemented are bookmarking, reviewing, and recommending. Bookmark allows users to save shows and not lose track of new shows. Reviewing is to state opinions about a show for others to promote good shows. Recommendations to find more shows similar to what users are watching because it can be difficult to find shows by looking at the entire catalog of anime.

User Flow:
A new user will be brought to the home menu where they will find a simple list of anime to look at and click on or can search for shows. When they decide to bookmark or rate a anime they will be pushed to make an account before they can use these features. When they fill out the form and create an account, they will get a recommended section on the home screen. As well as have access to rating and bookmarking anime.

Technology:
bcrypt, flask, flask-wtf, ipython, Jinja2, SQLAlchemy, wtforms.
