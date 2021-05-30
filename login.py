from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Blueprint 

login_bp = Blueprint('login_bp', __name__)


# @login_bp.route('/users/<username>')
# def show_profile(username):
#     users = ['daniele', 'michael', 'john']
#     if username in users:
#         return render_template('profile.html', user=username)
#     else:
#         return render_template('profile.html', reg=users)



# @login_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     user = request.form["user"]
#     return redirect(url_for('login_bp.show_profile', username=user))

