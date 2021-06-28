from utils.util import get_session
from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, update
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from utils import log
from datetime import datetime
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

def _next():
    log('next')
    slots = getAllSlots()
    days = []
    input_date = strToDate(request.args.get("start_date"))

    end_date = input_date

    start_date = input_date-timedelta(days=3)

    delta = timedelta(days=1)

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta

    # get all slot booked for current user
    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]
    log('[weight_rooms] booking ids: ', bookings)

    today = datetime.today()
    end_weed = today+timedelta(days=7) #calculate a week today + 7
    # calculate total hours booked from user
    cursor = session.query(func.coalesce(func.sum(Slot.hour_to-Slot.hour_from), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:
        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)
        total_daily = cursor.scalar()
        # add temporary calculated field for current user
        slot.daily_reservations = total_daily
    
    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()))

def _previous():
    log('[previous]')
    slots = getAllSlots()
    days = []

    input_date = strToDate(request.args.get("start_date"))

    start_date = input_date-timedelta(days=5)
    end_date =  input_date-timedelta(days=2)

    delta = timedelta(days=1)

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta

    # get all slot booked for current user
    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]
    log('[weight_rooms] booking ids: ', bookings)

    today = datetime.today()
    end_weed = today+timedelta(days=7) #calculate a week today + 7
    # calculate total hours booked from user
    cursor = session.query(func.coalesce(func.sum(Slot.hour_to-Slot.hour_from), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:
        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)
        total_daily = cursor.scalar()
        # add temporary calculated field for current user
        slot.daily_reservations = total_daily

    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()))

@login_required # richiede autenticazione
def _weight_rooms():

    log('[weight_rooms] called')
    start_date = date.today()
    end_date = date.today()+timedelta(days=3)

    slots = getAllSlots()
    days = []
    delta = timedelta(days=1)

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta

    # get all slot booked for current user
    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]
    log('[weight_rooms] booking ids: ', bookings)

    today = datetime.today()
    end_weed = today+timedelta(days=7)
    # calculate total hours booked from user
    cursor = session.query(func.coalesce(func.sum(Slot.hour_to-Slot.hour_from), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:

        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)

        total_daily = cursor.scalar()

        # add temporary calculated field for current user
        slot.daily_reservations = total_daily

    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()  ))

@login_required # richiede autenticazione
def _select_slot():
    selected_slot =request.args.get("slot_id")

    # get slot from id
    slot = Slot.query.filter_by(id=selected_slot).first()
    log(slot)
    user = current_user

    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]

    is_booked = slot.id in bookings
    log('isBooked: ', is_booked)

    if (user.role == 'owner'):
        # prendiamo tutti gli gli utenti che hanno prenotato questo slot
        booking_list = session.query(Booking, User.email).filter_by(slot=slot.id, user=User.id).all()
        resp = make_response(render_template("booking_list.html", slot=slot,user=user, booking_list=booking_list))
    else:
        resp = make_response(render_template("reservation_modal.html", slot=slot, user=user, is_booked=is_booked))

    return resp

@login_required # richiede autenticazione
def _book_slot():
    log('[book_slot]')

    # get params from request args
    slot_id =request.args.get("slot_id")

    with get_session() as session:

        # start transaction
        booking = Booking(current_user.id, slot_id) # prenota slot

        session.add(booking)

        query = session.query(Slot).filter_by(id=slot_id).first()

        query.places = query.places-1
        log('[book_slot] oldPlaces: ', query.places)
    
        # end transaction

    return redirect(url_for('weight_rooms'))

@login_required # richiede autenticazione
def _booking_list():

    booking_list = session.query(Booking, User.email, Slot.date, Slot.hour_from, Slot.hour_to, Slot.id).filter(Booking.user==User.id, Booking.slot==Slot.id).order_by(Slot.date)
    log(booking_list)

    return make_response(render_template("total_booking_list.html", user=current_user, booking_list=booking_list))

@login_required # richiede autenticazione
def _unbook_slot():
    # get params from request args
    slot_id =request.args.get("slot_id")
    log('unbook_slot id: ', slot_id)
    log('unbook_slot user id: ', current_user.id)
    # book slot for this user
    # start transaction
    with get_session() as session:

        # elimina prenotazione slot
        session.query(Booking).filter_by(slot=slot_id).delete()

        query = session.query(Slot).filter_by(id=slot_id).first()

        # si è liberato il posto, aggiungerlo ai disponibili
        query.places = query.places+1
        log('[unbook_slot] oldPlaces: ', query.places)
        # end transaction

    return redirect(url_for('weight_rooms'))

def get_week_limit():
    weight_room = session.query(WeightRoom).first()
    limit = weight_room.week_limit
    if (limit== None):
        limit = 99999999
    return limit

def get_daily_limit():
    weight_room = session.query(WeightRoom).first()
    limit = weight_room.daily_limit
    if (limit== None):
        limit = 99999999
    return limit

def getAllSlots():
    slots = session.query(Slot).all()

    return slots

def strToDate(date_str):
    date_str = date_str.split("-", 2)
    new_date = date(int(date_str[0]), int(date_str[1]), int(date_str[2]))
    return new_date

if __name__ == '__main__':
    app.run()