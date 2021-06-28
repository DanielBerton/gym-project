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
from datetime import timedelta
from utils import log
from datetime import datetime
from sqlalchemy import DDL, event
from flask import Blueprint 

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})

courses_bp = Blueprint('courses_bp', __name__)

metadata = MetaData()
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine, autoflush=True)
session = Session()

db = SQLAlchemy(app, session_options={"autoflush": True})

@courses_bp.route('/courses', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def courses():
    
    status = request.args.get("status")
    # order by start course
    courses=session.query(Instructor.name.label("instructor_name") , Instructor.surname.label("instructor_surname"), Course.id.label("course_id"), CourseScheduling.id, CourseScheduling.places, CourseScheduling.day_of_week,  CourseScheduling.start_hour, CourseScheduling.end_hour, Course.name).filter(Course.id == CourseScheduling.course, Instructor.id == Course.instructor ).order_by(CourseScheduling.start_hour)

    days = []
    log(courses)
    start_date = datetime.today()
    end_date = start_date+timedelta(days=6 )
    
    delta = timedelta(days=1)

    while start_date <= end_date:
        days.append(Calendar(date=start_date, day=start_date.day, month=start_date.strftime("%B"), day_name=start_date.strftime('%A')))  
        start_date += delta

    booked_course = [r.course_scheduling for r in session.query(BookingCourse.course_scheduling).filter_by(member=current_user.id)]

    # if owner get all course reservation
    if (current_user.role == 'owner'):
        all_bookings = session.query(BookingCourse.id, CourseScheduling.id, Course.name, Member.email, CourseScheduling.day_of_week) .filter(BookingCourse.member == Member.id, BookingCourse.course_scheduling == CourseScheduling.id, CourseScheduling.course == Course.id).all()

        log(all_bookings)
        return make_response(render_template("courses.html", user=current_user, route=request.path, courses=courses, days=days, booked_course=booked_course, status=status, all_bookings=all_bookings))

    return make_response(render_template("courses.html", user=current_user, route=request.path, courses=courses, days=days, booked_course=booked_course, status=status))

@courses_bp.route('/book_course', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def book_course():
    select_course =request.args.get("course_id")

    # start transaction
    with get_session() as session:
        booking = BookingCourse(current_user.id, select_course) # prenota slot

        session.add(booking)

        course_scheduling = session.query(CourseScheduling).filter_by(id=select_course).first()
 
        course_scheduling.places = course_scheduling.places-1
        log('[book_course] oldPlaces: ', course_scheduling.places)
        # end transaction

        # set status to shouw popup to user
        status = 'booked'
    return redirect(url_for('courses_bp.courses', status=status))     

@courses_bp.route('/unbook_course', methods=['GET', 'POST'])
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
        # set status to shouw popup to user
        status = 'unbooked'
    return redirect(url_for('courses_bp.courses', status=status))


if __name__ == '__main__':
    app.run()