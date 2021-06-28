from utils.util import get_session
from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, update
from flask_bootstrap import Bootstrap
from utils import log
from sqlalchemy import DDL, event, func
from flask import Blueprint 


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})

settings_bp = Blueprint('settings_bp', __name__)

metadata = MetaData()
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine, autoflush=True)
session = Session()

db = SQLAlchemy(app, session_options={"autoflush": True})

@settings_bp.route('/setting', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def setting():
    log(current_user.role)
    # bloccare se utente non è owner
    if current_user.role != 'owner':
         return redirect(url_for('unauthorized'))
   
    courses = session.query(Course).all()
    weight_rooms = db.session.query(WeightRoom).all()

    # get week_limit and daily_limit
    week_limit = weight_rooms[0].week_limit
    daily_limit = weight_rooms[0].daily_limit
    log(weight_rooms)

    return make_response(render_template("setting.html", weight_rooms=weight_rooms, route=request.path, courses=courses, user=current_user, week_limit=week_limit, daily_limit=daily_limit))

@settings_bp.route('/update_weight_room', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def update_weight_room():
    
    if request.method == 'POST':
        # get params from form
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
    
    return redirect(url_for('settings_bp.setting'))

@settings_bp.route('/update_course', methods=['GET', 'POST'])
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
    
    return redirect(url_for('settings_bp.setting'))

@settings_bp.route('/set_week_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_week_limit():
    week_limit = request.form['week_limit']
    log('set_week_limit', week_limit)

    with get_session() as session:
        gym = session.query(Gym).filter_by(owner=current_user.id).first()

        weight_rooms = session.query(WeightRoom).filter_by(gym=gym.id).all()

        for weight_room in weight_rooms :
            print(weight_room)
            weight_room.week_limit = week_limit

        #session.commit()
    
    return redirect(url_for('settings_bp.setting'))

@settings_bp.route('/set_daily_limit', methods=['GET', 'POST'])
@login_required # richiede autenticazione
def set_daily_limit():
    
    daily_limit = request.form['daily_limit']
    log('set_daily_limit', daily_limit)

    with get_session() as session:
        # start transaction
        gym = session.query(Gym).filter_by(owner=current_user.id).first()

        weight_rooms = session.query(WeightRoom).filter_by(gym=gym.id).all()

        for weight_room in weight_rooms :
            print(weight_room)
            weight_room.daily_limit = daily_limit

        #session.commit()
    return redirect(url_for('settings_bp.setting'))


if __name__ == '__main__':
    app.run()