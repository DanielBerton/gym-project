from views.weight_room import _previous, _next, _weight_rooms,  _select_slot, _book_slot, _unbook_slot
from views.courses import _courses, _unbook_course, _book_course
from views.settings import _setting, _set_daily_limit, _set_week_limit, _update_course, _update_weight_room
from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, update
from flask_bootstrap import Bootstrap
from utils import log
from sqlalchemy import DDL, event, func


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})

app.register_blueprint(login_bp)

metadata = MetaData()
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine, autoflush=True)
session = Session()

db = SQLAlchemy(app, session_options={"autoflush": True})

def get_user_by_email(email):
    log('[get_user_by_email] executed', '')
    user = User.query.filter_by (email=email).first()
    log('[get_user_by_email] user: ', user)
    return user

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

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    log('[logout] executed', '')
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login ():
    log('[login] executed')
    if request.method == 'POST':

        email = request.form['user']

        user = User.query.filter_by(email=email).first()

        log('[login] user: ',  user)
        if (user and user.password is not None):
            log('[login]', 'OK ' + request.form['password']+ '  ' +user.password)
            if request.form['password'] == user.password:
                users = get_user_by_email(request.form['user'])
                login_user(users)
                return redirect(url_for('private'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/bookink_list', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def bookink_list():

    booking_list = session.query(Booking, User.email, Slot.date, Slot.hour_from, Slot.hour_to, Slot.id).filter(Booking.user==User.id, Booking.slot==Slot.id).order_by(Slot.date)
    log(booking_list)

    return make_response(render_template("total_booking_list.html", user=current_user, booking_list=booking_list))

@app.route('/next', methods=['GET', 'POST'])
def next():
    return _next()

@app.route('/previous', methods=['GET', 'POST'])
def previous():
    return _previous()
    
@app.route('/weight_rooms', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def weight_rooms():
    return _weight_rooms()

@app.route('/courses', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def courses():
    return _courses()

@app.route('/book_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def book_course():
    return _book_course()

@app.route('/unbook_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def unbook_course():
    return _unbook_course()

@app.route('/select_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def select_slot():
    return _select_slot()

@app.route('/book_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def book_slot():
    return _book_slot()

@app.route('/unbook_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def unbook_slot():
    return _unbook_slot()

@app.route('/setting', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def setting():
    return _setting()

@app.route('/update_weight_room', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_weight_room():
    return _update_weight_room()

@app.route('/update_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_course():
    return _update_course()

@app.route('/set_week_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_week_limit():
    return _set_week_limit()

@app.route('/set_daily_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_daily_limit():
    
    return _set_daily_limit()

if __name__ == '__main__':
    app.run()

    from views import *
    
