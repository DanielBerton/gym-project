from flask import Flask
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from sqlalchemy import *
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metadata = MetaData()

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __table_args__ = (
        db.UniqueConstraint('email', 'role', name='uniq_exec_email_role'),
        db.Index('user_email_index', 'email'),
        db.CheckConstraint('role IN ("owner", "user", "instructor")', name='user_role_list'),
    )
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))
    role = db.Column(db.String(50), nullable=False)

    def __init__(self, id, email, password, role):
        self.id = id
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s', role='%s')>" % (self.id, self.email, '*****', self.role)


class Owner(User):
    __tablename__ = 'owner'
    __mapper_args__ = {'polymorphic_identity': 'user'}
    __table_args__ = (
        db.CheckConstraint('(name NOT NULL) and (surname NOT NULL) or (company_name NOT NULL)', name='name_and_surname_or_company_name'),
    )
    id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)

    def __init__(self, id, email, password, role, name, surname, company_name):
        super().__init__(id, email, password, role)
        self.name = name
        self.surname = surname
        self.company_name = company_name


    def __repr__(self):
        return "<Owner(id='%s', email='%s', password='%s', name='%s', role='%s')>" % (self.id, self.email, self.password, self.name, self.role)

class Member(User, db.Model):
    __tablename__ = 'member'
    id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)

    def __repr__(self):
        return "<Member(id='%s', email='%s', password='%s', name='%s', role='%s')>" % (self.id, self.email, self.password, self.name, self.role)

class Instructor(User, db.Model):
    __tablename__ = 'instructor'
    id = db.Column(Integer, ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(100))

    def __init__(self, id, email, password, role, name, surname, specialization):
        super().__init__(id, email, password, role)
        print('inside super: '+ specialization)
        self.name = name
        self.surname = surname
        self.specialization = specialization

    def __repr__(self):
        return "<Instructor(id='%s', email='%s', password='%s', role='%s', name='%s', surname='%s', specialization='%s')>" % (self.id, self.email, self.password, self.role, self.name, self.surname, self.specialization)


class Gym(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    zipCode = db.Column(db.String(100))
    country = db.Column(db.String(100))
    owner = db.Column(Integer, ForeignKey('owner.id'))

    def __init__(self, id, name, address, city, zipCode, country, owner):
        self.id = id
        self.name = name
        self.address = address
        self.city = city
        self.zipCode = zipCode
        self.country = country
        self.owner = owner

class WeightRoom(db.Model):
    __tablename__ = 'weight_room'
    __table_args__ = (
        db.UniqueConstraint('name', name='uniq_weight_room_name'),
        db.CheckConstraint('(size > 0)', name='weight_room_minimum_size'),
    )
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    size = db.Column(db.Integer)
    places = db.Column(db.Integer)
    week_limit = db.Column(db.Integer, nullable=True)
    daily_limit = db.Column(db.Integer, nullable=True)
    gym = db.Column(Integer, ForeignKey('gym.id'))

    def __init__(self, id, name, size, places, week_limit, daily_limit, gym):
        self.id = id
        self.name = name
        self.size = size
        self.places = places
        self.week_limit = week_limit
        self.daily_limit = daily_limit
        self.gym = gym

    def __repr__(self):
        return "<WeightRoom(id='%s', name='%s', size='%s',  places='%s', gym='%s'gym)>" % (self.id, self.name, self.size,  self.places, self.gym)

class Slot(db.Model):
    __tablename__ = 'slot'
    __table_args__ = (
        db.Index('slot_date_index', 'date'),
    )
    id = db.Column('id', db.Integer, primary_key = True)
    day = db.Column(db.Integer)
    date = db.Column(db.Date)
    hour_from = db.Column(db.String(100))
    hour_to = db.Column(db.String(100))
    places = db.Column(db.Integer)
    weight_room = db.Column(Integer, ForeignKey('weight_room.id'))

    def __init__(self, day, date, hour_from, hour_to, places, weight_room ):
        self.day = day
        self.date = date
        self.hour_from = hour_from
        self.hour_to = hour_to
        self.places = places
        self.weight_room  = weight_room

    def __repr__(self):
        return "<Slot(id='%s', day='%d', date='%s', hour_from='%s', hour_to='%s', places='%d', weight_room ='%d')>" % (self.id, self.day, self.date, self.hour_from, self.hour_to, self.places, self.weight_room )

# Gym slot booking
class Booking(db.Model):
    __tablename__ = 'booking'
    __table_args__ = (
        db.Index('booking_user_index', 'user'),
    )
    id = db.Column('id', db.Integer, primary_key = True, autoincrement=True)
    user = db.Column(Integer, ForeignKey('user.id'))
    slot = db.Column(Integer, ForeignKey('slot.id'))

    def __init__(self, user, slot):
        self.user = user
        self.slot = slot
    
    def __repr__(self):
        return "<Booking(id='%s', user='%s', slot='%s')>" % (self.id, self.user, self.slot)

## Start course ##
class Course(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    places = db.Column(db.Integer)
    gym = db.Column(Integer, ForeignKey('gym.id'))
    instructor = db.Column(Integer, ForeignKey('instructor.id'))

    def __init__(self, id, name, places, gym, instructor):
        self.id = id
        self.name = name
        self.places = places
        self.gym = gym
        self.instructor = instructor

class CourseScheduling(db.Model):
    __tablename__ = 'course_scheduling'
    __table_args__ = (
        db.Index('course_scheduling_start_hour_index', 'start_hour'),
    )
    id = db.Column('id', db.Integer, primary_key = True)
    day_of_week = db.Column(db.String(50))
    start_hour = db.Column(db.String(50))
    end_hour = db.Column(db.String(50))
    places = db.Column(db.Integer)
    course = db.Column(Integer, ForeignKey('course.id'))

    def __init__(self, day_of_week, start_hour, end_hour, places, course):
            self.day_of_week = day_of_week
            self.start_hour = start_hour
            self.end_hour = end_hour
            self.places = places
            self.course = course
    
    def __repr__(self):
        return "<CourseScheduling(id='%s', day_of_week='%s', start_hour='%s',  end_hour='%s', places='%s', course='%s')>" % (self.id, self.day_of_week, self.start_hour,  self.end_hour, self.places, self.course)

# booking_course
class BookingCourse(db.Model):
    __tablename__ = 'booking_course'
    id = db.Column('id', db.Integer, primary_key = True, autoincrement=True)
    member = db.Column(Integer, ForeignKey('member.id'))
    course_scheduling = db.Column(Integer, ForeignKey('course_scheduling.id'))

    def __init__(self, member, course_scheduling):
            self.member = member
            self.course_scheduling = course_scheduling
    
    def __repr__(self):
        return "<BookingCourse(id='%d', member='%s', course_scheduling='%s')>" % (self.id, self.member, self.course_scheduling)

class Calendar:
    def __init__(self, date, day, month, day_name):
        self.date = date
        self.day = day
        self.month = month
        self.day_name = day_name