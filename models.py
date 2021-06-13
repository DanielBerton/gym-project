from flask import Flask
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.register_blueprint(login_bp)

metadata = MetaData()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))  

    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s')>" % (self.id, self.email, self.password)