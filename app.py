from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, login_user, logout_user
from login import login_bp
from weight_room import wr_bp
from settings import settings_bp
from courses import courses_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, update
from flask_bootstrap import Bootstrap
from utils import log
from sqlalchemy import DDL, event, func
from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=False, connect_args={'check_same_thread': False})
# echo shows query and executions, set true just for development 

# Register on blueprints
app.register_blueprint(login_bp)
app.register_blueprint(wr_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(courses_bp)

metadata = MetaData()
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine, autoflush=True)
session = Session()

db = SQLAlchemy(app, session_options={"autoflush": True})

@login_manager.user_loader # definisce la callback
def load_user(user_id):

    log('[load_user] user_id: ', user_id)
    user = User.query.filter_by(id=user_id).first()
    log('[load_user] Logged user: ',user)
    return user

@app.route('/')
def home ():
    log('[home] executed')
    # current_user identifica l'utente attuale 
    # # utente anonimo prima dell'autenticazione 
    log(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('private')) 
    return render_template("login.html", route='login')

@app.route('/private')
@login_required # richiede autenticazione
def private ():
    
    if current_user.is_authenticated:
        log('is_authenticated')
        user = current_user
    log('[private] executed')
    users = User.query.all()
    log('[private] users ', users)

    # check role, if owner go to admin_dashboard, else standard private page
    if (user.role == 'owner'):
        resp = make_response(render_template("admin_dashboard.html", users=users, user=user, route=request.path))
    else:
        resp = make_response(render_template("private.html", users=users, user=user, route=request.path))

    golden = session.query(Gym).join(WeightRoom).filter(Gym.id == WeightRoom.gym, Gym.id == 1).first()

    log('[private] golden: ', golden)
    return resp

@app.route('/unauthorized', methods=['GET', 'POST'])
@login_manager.unauthorized_handler
def unauthorized():
    log('[unauthorized] called', current_user)
    return make_response(render_template("unauthorized.html", route=request.path))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def admin_dashboard():
    log(request.path )
    return make_response(render_template("admin_dashboard.html", user=current_user, route=request.path))


if __name__ == '__main__':
    app.run()

    