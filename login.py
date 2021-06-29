from flask import request
from flask import redirect
from flask import url_for, escape
from flask import Blueprint 
from flask_login import login_user
from werkzeug.utils import escape
from models import *
from utils.log import log

login_bp = Blueprint('login_bp', __name__)

def get_user_by_email(email):
    log('[get_user_by_email] executed', '')
    user = User.query.filter_by (email=email).first()
    log('[get_user_by_email] user: ', user)
    return user

@login_bp.route('/login', methods=['GET', 'POST'])
def login ():
    log('[login] executed')
    if request.method == 'POST':
        
        email = escape(request.form['user'])
        user = User.query.filter_by(email=email).first()
        password = escape(request.form['password'])
        log('[login] user: ',  user)
        if (user and user.password is not None):
            log('[login]', 'OK ' + password+ '  ' +user.password)
            # check password from user retrieve from database
            if password == user.password:
                # retrieve user by email
                users = get_user_by_email(email)
                # save user on session and go to private page
                login_user(users)
                return redirect(url_for('private'))
        else:
            return redirect(url_for('home')) # login failed
    else:
        return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
@login_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    log('[logout] executed', '')
    # remove user from session
    logout_user() 
    return redirect(url_for('home'))


