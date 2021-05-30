from flask import Flask
from flask_login import *
from sqlalchemy import *


app = Flask(__name__)

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, pwd):
        self.id = id 
        self.email = email 
        self.pwd = pwd


@login_manager.user_loader # definisce la callback
def load_user(user_id):
    conn = engine.connect()
    rs = conn.execute('SELECT * FROM Users WHERE id = ?', user_id) 
    user = rs.fetchone()
    conn.close()
    return User(user.id, user.email, user.pwd)