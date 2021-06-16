from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join
from sqlalchemy.sql import select

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True)

app.register_blueprint(login_bp)

metadata = MetaData()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine)
session = Session()

db = SQLAlchemy(app)


@app.route('/private')
@login_required # richiede autenticazione
def private ():

    if current_user.is_authenticated:
        log('is_authenticated')
        user = current_user
    log('[private] executed')
    users = Users.query.all()
    log('[private] users ', users)

    if (user.role == 'admin'):
        resp = make_response(render_template("admin_dashboard.html", users=users, user=user))
    else:
        resp = make_response(render_template("private.html", users=users, user=user))
    #gyms = session.query(Gym, WeightRoom).filter(Gym.id==WeightRoom.gym).all()

    golden = session.query(Gym).join(WeightRoom).filter(Gym.id == WeightRoom.gym).first()

    # gyms = Gym.query.all()
    log(golden)
    return resp


def log(method, message=''):
    print('---------------------------------')
    print(method, message)
    print('---------------------------------')
