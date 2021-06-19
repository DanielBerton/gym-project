from typing import ContextManager
from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, load_only
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join
from sqlalchemy.sql import select
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from contextlib import contextmanager


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

Session = sessionmaker(bind = engine)
session = Session()

db = SQLAlchemy(app)

def get_user_by_email(email):
    log('[get_user_by_email] executed', '')
    user = Users.query.filter_by (email=email).first()
    log('[get_user_by_email] user: ', user)
    return user

@login_manager.user_loader # definisce la callback
def load_user(user_id):

    log('[load_user] user_id: ', user_id)
    user = Users.query.filter_by(id=user_id).first()
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
    return render_template("login.html")

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

@app.route('/weight_rooms', methods=['GET', 'POST'])
def weight_rooms():
    #slots = Slot.query.group_by(Slot.day).all()
    slots = session.query(Slot).all()
    days = []
    start_date = date(2021, 7, 1)
    end_date = date(2021, 7, 7)
    delta = timedelta(days=1)

    print('------------------------------ SLOTS ------------------------------')
    for s in slots:
        if (s.places <50):
            print('Slot after with id %d:  places %d', s.id, s.places)

    while start_date <= end_date:
        days.append(Calendar(day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        # print(start_date.day)
        # print(start_date.strftime('%A'))
        #print(start_date.strftime("%Y-%m-%d")+ start_date.strftime('%A') )
        start_date += delta

    # get all slot booked for current user
    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]
    log('[weight_rooms] booking ids: ', bookings)
    return make_response(render_template("weight_rooms.html", slots=slots,days=days, bookings=bookings ))

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    return make_response(render_template("courses.html"))

@app.route('/select_slot', methods=['GET', 'POST'])
def select_slot():
    selected_slot =request.args.get("slot_id")

    # get slot from id
    slot = Slot.query.filter_by(id=selected_slot).first()
    log(slot)
    user = current_user
    resp = make_response(render_template("reservation_modal.html", slot=slot, user=user))
    return resp

@app.route('/book_slot', methods=['GET', 'POST'])
def book_slot():
    slot_id =request.args.get("slot_id")
    log('book_slot id: ', slot_id)
    log('book_slot user id: ', current_user.id)
    # book slot for this user
    # start transaction
    with get_session() as session:
        
        booking = Booking(current_user.id, slot_id) # prenota slot

        db.session.add(booking)
        #db.session.commit()

        query = session.query(Slot).filter_by(id=slot_id).first()

        query.places = query.places-1
        log('[book_slot] oldPlaces: ', query.places)
        # end transaction
        db.session.commit()


    return redirect(url_for('weight_rooms'))

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

        user = Users.query.filter_by(email=email).first()

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

@app.route('/test')
def test():
    u = request.args.get('Users')
    #usafe
        #return "Welcome {}".format(u)
    #safe non viene interpretato come html
    return render_template('profile.html', Users=u)

@contextmanager
def get_session():
    session = db.session

    try:
        yield session
    except:
        session.rollback()
        raise
    else:
        session.commit()

if __name__ == '__main__':
    app.run()

# Logger method
# param message is optional
def log(method, message=''):
    print('---------------------------------')
    print(method, message)
    print('---------------------------------')
