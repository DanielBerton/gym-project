from typing import ContextManager
from utils.util import get_session
from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, load_only, aliased
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, update
from sqlalchemy.sql import select
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from contextlib import contextmanager
from utils import log, transaction
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

    if (user.role == 'owner'):
        resp = make_response(render_template("admin_dashboard.html", users=users, user=user, route=request.path))
    else:
        resp = make_response(render_template("private.html", users=users, user=user, route=request.path))
    #gyms = session.query(Gym, WeightRoom).filter(Gym.id==WeightRoom.gym).all()

    golden = session.query(Gym).join(WeightRoom).filter(Gym.id == WeightRoom.gym).first()

    # gyms = Gym.query.all()
    log(golden)
    return resp

@app.route('/next', methods=['GET', 'POST'])
def next():
    log('next')
    slots = session.query(Slot).all()
    days = []

    date_str =request.args.get("start_date").split("-", 2)
    s = date(int(date_str[0]), int(date_str[1]), int(date_str[2]))
    end_date = s

    start_date = s-timedelta(days=3)

    print('------------------------------ LOOOOOOOOOK ------------------------------')
    print(start_date)
    print(end_date)
    
    # start_date = start_date+timedelta(days=1)
    # end_date = end_date+timedelta(days=1)
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
    cursor = session.query(func.coalesce(func.sum(Slot.hourTo-Slot.hourFrom), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:
        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)
        total_daily = cursor.scalar()
        # add temporary calculated field for current user
        slot.daily_reservations = total_daily

    
    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()))

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

@app.route('/previous', methods=['GET', 'POST'])
def previous():
    log('previous')
    slots = session.query(Slot).all()
    days = []

    date_str =request.args.get("start_date").split("-", 2)
    s = date(int(date_str[0]), int(date_str[1]), int(date_str[2]))
    end_date = s

    start_date = s-timedelta(days=5)
    end_date = s-timedelta(days=2)

    print('------------------------------ LOOOOOOOOOK ------------------------------')
    print(start_date)
    print(end_date)
    
    # start_date = start_date+timedelta(days=1)
    # end_date = end_date+timedelta(days=1)
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
    cursor = session.query(func.coalesce(func.sum(Slot.hourTo-Slot.hourFrom), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:
        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)
        total_daily = cursor.scalar()
        # add temporary calculated field for current user
        slot.daily_reservations = total_daily

    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()))

@app.route('/weight_rooms', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def weight_rooms():

    start_date = date.today()
    end_date = date.today()+timedelta(days=3)

    print(start_date)
    slots = session.query(Slot).all()
    days = []
    delta = timedelta(days=1)
    print('------------------------------ SLOTS ------------------------------')

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta

    # get all slot booked for current user
    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]
    log('[weight_rooms] booking ids: ', bookings)

    today = datetime.today()
    end_weed = today+timedelta(days=7)
    # calculate total hours booked from user
    cursor = session.query(func.coalesce(func.sum(Slot.hourTo-Slot.hourFrom), 0)).filter(Slot.id == Booking.slot, Booking.user == current_user.id, Slot.date > today.strftime('%Y-%m-%d'), Slot.date < end_weed.strftime('%Y-%m-%d'))
    total_week = cursor.scalar()
    log(datetime.today().strftime('%Y-%m-%d'))
    log(total_week)

    for slot in slots:

        cursor = session.query(func.count(Booking.id)).filter(Booking.user == current_user.id, Slot.id == Booking.slot, Slot.date == slot.date)

        total_daily = cursor.scalar()
        log('================================================================================================================================================')
        log('================================================================================================================================================')
        log('================================================================================================================================================')
        log('================================================================================================================================================')
        log('----------------------------------------------------------------', total_daily)
        # add temporary calculated field for current user
        slot.daily_reservations = total_daily

    return make_response(render_template("weight_rooms.html", user=current_user, slots=slots,days=days, bookings=bookings, route=request.path, start_date=start_date, end_date=end_date, total_week=total_week, total_daily=total_daily, week_limit=get_week_limit(), daily_limit=get_daily_limit()  ))

@app.route('/courses', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def courses():
    
    status = request.args.get("status")
    # order by start course
    courses=session.query(Course.id.label("course_id"), CourseScheduling.id, CourseScheduling.places, CourseScheduling.day_of_week,  CourseScheduling.start_hour, CourseScheduling.end_hour, Course.name).filter(Course.id == CourseScheduling.course).order_by(CourseScheduling.start_hour)

    days = []
    print('Before #########################################')
    start_date = date(2021, 7, 1)
    end_date = date(2021, 7, 7)

    # start_date = date.today()
    # end_date = date.today()+timedelta(days=4)

    delta = timedelta(days=1)

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta


    booked_course = [r.course_scheduling for r in session.query(BookingCourse.course_scheduling).filter_by(member=current_user.id)]

    log(booked_course)
    return make_response(render_template("courses.html", user=current_user, route=request.path, courses=courses, days=days, booked_course=booked_course, status=status))

@app.route('/book_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def book_course():
    select_course =request.args.get("course_id")

    # start transaction
    with get_session() as session:
        booking = BookingCourse(current_user.id, select_course) # prenota slot

        session.add(booking)
        session.commit()

        #b = db.session.query(BookingCourse).all()
        print(booking)
        course_scheduling = session.query(CourseScheduling).filter_by(id=select_course).first()
        #query = session.query(CourseScheduling).filter_by(id=course_scheduling_id).first()

        course_scheduling.places = course_scheduling.places-1
        log('[book_course] oldPlaces: ', course_scheduling.places)
        # end transaction
        session.commit()
    status = 'booked'
    return redirect(url_for('courses', status=status))     

@app.route('/unbook_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def unbook_course():
    select_course =request.args.get("course_id")
    log('unbook_course id: ', select_course)
    log('unbook_course user id: ', current_user.id)
    # book slot for this user
    # start transaction
    with get_session() as session:

        # elimina prenotazione slot
        session.query(BookingCourse).filter_by(course_scheduling=select_course).delete()

        query = session.query(CourseScheduling).filter_by(id=select_course).first()

        # si è liberato il posto, aggiungerlo ai disponibili
        query.places = query.places+1
        log('[unbook_course] oldPlaces: ', query.places)
        # end transaction
        db.session.commit()
    status = 'unbooked'
    return redirect(url_for('courses', status=status))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def admin_dashboard():
    log(request.path )
    return make_response(render_template("admin_dashboard.html", user=current_user, route=request.path))

@app.route('/select_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def select_slot():
    selected_slot =request.args.get("slot_id")

    # get slot from id
    slot = Slot.query.filter_by(id=selected_slot).first()
    log(slot)
    user = current_user

    bookings = [r.slot for r in session.query(Booking.slot).filter_by(user=current_user.id)]

    is_booked = slot.id in bookings
    log('isBooked: ', is_booked)


    if (user.role == 'owner'):
        # prendiamo tuttgli gli utenti che hanno prenotato questo slot
        booking_list = session.query(Booking, User.email).filter_by(slot=slot.id, user=User.id).all()
        resp = make_response(render_template("booking_list.html", slot=slot,user=user, booking_list=booking_list))
    else:
        resp = make_response(render_template("reservation_modal.html", slot=slot, user=user, is_booked=is_booked))

    return resp

@app.route('/book_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def book_slot():
    log('############################################### book_slot ###############################################')
    slot_id =request.args.get("slot_id")



    cursor = session.query(func.sum(Slot.hourTo-Slot.hourFrom)).filter(Slot.id == Booking.slot, Booking.user == current_user.id)
    total = cursor.scalar()
    log('Sum of hours booked : ', total)

    # get related slot from Booking slot
    slot = session.query(Slot).filter(Slot.id==slot_id).first()
    log('================================================================================================================================================')
    log('================================================================================================================================================')
    log(slot_id)
    log('================================================================================================================================================')
    log('================================================================================================================================================')

    # get weight room by id (from related slot)
    weight_room = session.query(WeightRoom).filter_by(id=slot.weight_room).first()

    # if (weight_room.week_limit != None and total > weight_room.week_limit):
    #     log('limit exceeded')
        

    # book slot for this user
    # start transaction
    booking = Booking(current_user.id, slot_id) # prenota slot

    session.add(booking)
    #db.session.commit()

    query = session.query(Slot).filter_by(id=slot_id).first()

    query.places = query.places-1
    log('[book_slot] oldPlaces: ', query.places)
    # end transaction
    session.commit()


    return redirect(url_for('weight_rooms'))


#@event.listens_for(Booking, 'before_insert')
def week_limit_func(mapper, connection, booking):

    cursor = session.query(func.sum(Slot.hourTo-Slot.hourFrom)).filter(Slot.id == Booking.slot, Booking.user == booking.user)
    total = cursor.scalar()
    log('Sum of hours booked : ', total)

    log(mapper)
    user_bookings = session.query(Booking).filter_by(user=booking.user).count()

    # get related slot from Booking slot
    slot = session.query(Slot).filter(Slot.id==booking.slot).first()

    # get weight room by id (from related slot)
    weight_room = session.query(WeightRoom).filter_by(id=slot.weight_room).first()

    if (weight_room.week_limit != None and total > weight_room.week_limit):
        log('inside if')
            #elimina prenotazione slot
        session.query(Booking).filter_by(slot=booking.slot).delete()

        query = session.query(Slot).filter_by(id=booking.slot).first()

        # si è liberato il posto, aggiungerlo ai disponibili
        # query.places = query.places+1
        # log('[unbook_slot] oldPlaces: ', query.places)
        #end transaction
        
        #always close transaction and commit
        #session.commit()
        # https://stackoverflow.com/questions/25792332/sqlalchemy-after-insert-doesnt-update-target-object-fields/27483133


        log(query)
        log('################################################################################################################################################')
        log('################################################################################################################################################')
        log('################################################################################################################################################')
        log('################################################################################################################################################')
        log(booking.slot)
        #query_delete = 'delete from booking where slot IN  (37, 46, 55, 64)'
        query_delete_2 = 'delete from booking where slot = '+booking.slot
        log(query_delete_2)
        connection.execute(query_delete_2)
        booking_table = Booking.__table__
        slot_table = Slot.__table__

        connection.execute(booking_table.delete().where(booking_table.c.slot==booking.slot))
        #connection.execute("DELETE FROM booking")

        connection.execute(
            slot_table.update().
            where(slot_table.c.id==booking.slot).
            values(places=query.places+1)
        )
        #session.commit()
        return redirect(url_for('weight_rooms'))
    else:
        log('inside else')
        #session.commit()


#@event.listens_for(Booking, 'after_insert')
def week_limit_func(mapper, connection, booking):
    
    log(booking)
    log(mapper)
    log(connection)
    cursor = session.query(func.sum(Slot.hourTo-Slot.hourFrom)).filter(Slot.id == Booking.slot, Booking.user == booking.user)
    total = cursor.scalar()
    log('Sum of hours booked : ', total)

    user_bookings = session.query(Booking).filter_by(user=booking.user).count()

    # get related slot from Booking slot
    slot = session.query(Slot).filter(Slot.id==booking.slot).first()

    # get weight room by id (from related slot)
    weight_room = session.query(WeightRoom).filter_by(id=slot.weight_room).first()

    log('my_func2  called: ', user_bookings)
    log('################################################################################################################################################')
    log(weight_room.id)
    log(weight_room.week_limit)
    log('weight_room_id --> ', slot.weight_room)
    

    if (weight_room.week_limit != None and total > weight_room.week_limit):
        log('inside if')
            #elimina prenotazione slot
        session.query(Booking).filter_by(slot=booking.slot).delete()

        query = session.query(Slot).filter_by(id=booking.slot).first()

        # si è liberato il posto, aggiungerlo ai disponibili
        query.places = query.places+1
        log('[unbook_slot] oldPlaces: ', query.places)
        #end transaction
        
        #always close transaction and commit
        session.commit()
    else:
        log('inside else')
        session.commit()
    

@app.route('/unbook_slot', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def unbook_slot():
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
        session.commit()


    return redirect(url_for('weight_rooms'))

@app.route('/setting', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def setting():
    
    #courses=session.query(Course.id.label("course_id"), CourseScheduling.id, CourseScheduling.places, CourseScheduling.day_of_week,  CourseScheduling.start_hour, CourseScheduling.end_hour, Course.name).filter(Course.id == CourseScheduling.course).order_by(CourseScheduling.start_hour)
    courses = session.query(Course).all()
    weight_rooms = db.session.query(WeightRoom).all()

    week_limit = weight_rooms[0].week_limit
    daily_limit = weight_rooms[0].daily_limit
    log(weight_rooms)
    # fare join con Gym e con proprietario
    
    return make_response(render_template("setting.html", weight_rooms=weight_rooms, route=request.path, courses=courses, user=current_user, week_limit=week_limit, daily_limit=daily_limit))


@app.route('/update_weight_room', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_weight_room():
    
    if request.method == 'POST':

        name = request.form['name']
        size = request.form['size']
        places = request.form['places']
        id = request.form['id']

        with get_session() as session:
            wr = session.query(WeightRoom).filter_by(id=id).first()
            wr.places = places
            wr.size = size
            wr.name = name

            slots = session.query(Slot).filter_by(weight_room=id).all()
            for slot in slots:
                slot.places = places
    
    return redirect(url_for('setting'))

@app.route('/update_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_course():
    
    if request.method == 'POST':

        course_name = request.form['course_name']
        course_places = request.form['course_places']
        course_id = request.form['id']

        with get_session() as session:
            wr = session.query(Course).filter_by(id=course_id).first()
            wr.places = course_places
            wr.name = course_name

            course_schedulings = session.query(CourseScheduling).filter_by(course=course_id).all()
            for course_scheduling in course_schedulings:
                course_scheduling.places = course_places
    
    return redirect(url_for('setting'))

@app.route('/set_week_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_week_limit():
    week_limit = request.form['week_limit']
    log('set_week_limit', week_limit)

    tbl = Table('booking', metadata)
    event.listen(tbl, 'after_create', DDL(("""
            CREATE TRIGGER update_task_state 
            AFTER INSERT ON booking
            BEGIN
                UPDATE slot SET places = 200 WHERE id = 37;
                DELETE FROM booking;
            END;
        """)))
    event.listen(
        Booking.__table__,
        'after_create',
        DDL("""
            CREATE TRIGGER update_places 
            AFTER INSERT ON booking
            BEGIN
                UPDATE slot SET places = '200' WHERE id = 37;
            END;
        """)
    )

    event.listen(
        Booking.__table__,
        'after_create',
        DDL("""
            CREATE TRIGGER update_places 
            AFTER INSERT ON booking
            BEGIN
                DELETE FROM booking;
            END;
        """)
    )

    with get_session() as session:
        gym = session.query(Gym).filter_by(owner=current_user.id).first()

        weight_rooms = session.query(WeightRoom).filter_by(gym=gym.id).all()

        for weight_room in weight_rooms :
            print(weight_room)
            weight_room.week_limit = week_limit

        session.commit()
    
    return redirect(url_for('setting'))



@app.route('/set_daily_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_daily_limit():
    
    daily_limit = request.form['daily_limit']
    log('set_daily_limit', daily_limit)

    with get_session() as session:
        gym = session.query(Gym).filter_by(owner=current_user.id).first()

        weight_rooms = session.query(WeightRoom).filter_by(gym=gym.id).all()

        for weight_room in weight_rooms :
            print(weight_room)
            weight_room.daily_limit = daily_limit

        session.commit()
    return redirect(url_for('setting'))

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

@app.route('/test')
def test():
    u = request.args.get('User')
    #usafe
        #return "Welcome {}".format(u)
    #safe non viene interpretato come html
    return render_template('profile.html', User=u)


if __name__ == '__main__':
    app.run()

    from views import *
