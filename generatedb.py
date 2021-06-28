from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.sqltypes import NullType
from models import Gym, User, Owner, Member, Instructor, WeightRoom, Slot, Booking, Course, CourseScheduling, BookingCourse 
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import as_declarative, has_inherited_table, declared_attr
import datetime
from datetime import date, timedelta
from models import *

app = Flask (__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

metadata = MetaData()

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
    #CHeck su role può essere solo owner, member eecc
    #__mapper_args__ = {'polymorphic_on': email }

    def __init__(self, id, email, password, role):
        self.id = id
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s', role='%s')>" % (self.id, self.email, self.password, self.role)


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
        db.CheckConstraint('(places <= size/2)', name='weight_room__size_places_ratio'),
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

admin = Owner(id=1, email='admin@gmail.com', password='admin', role='owner', name='admin', surname='admin', company_name='')
admin2 = Owner(id=20, email='admin2@gmail.com', password='admin2', role='owner', name='', surname='', company_name=None)
db.session.add_all([admin2])
gold_gym = Gym(id=1, name='Golden Gym', address='360 Hampton Dr', city='Venice', zipCode='90291', country='United States', owner=admin.id)

room_1 = WeightRoom(id=1, name='Room 1', size=85, places=35, week_limit=None, daily_limit=None, gym=gold_gym.id)

datetime_object = datetime.datetime.now()
start_date = date.today()-timedelta(days=4)
end_date = date(2021, 7, 31)
delta = timedelta(days=1)
while start_date <= end_date:
    db.session.add_all([
        Slot(day=start_date.day ,date=start_date, hour_from='9:00', hour_to='10:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='10:00', hour_to='11:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='12:00', hour_to='13:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='14:00', hour_to='15:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='16:00', hour_to='17:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day, date=start_date, hour_from='17:00', hour_to='18:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day, date=start_date, hour_from='18:00', hour_to='19:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='19:00', hour_to='20:00', places=room_1.places, weight_room =room_1.id),
        Slot(day=start_date.day ,date=start_date, hour_from='20:00', hour_to='21:00', places=room_1.places, weight_room =room_1.id),
    ])
    start_date += delta

###### Courses ########
instructor = Instructor(id=2, email='instructor@gmail.com', password='instructor', role='instructor', name='Mario', surname='Rossi', specialization='Zumba')
instructor_2 = Instructor(id=10, email='instructor2@gmail.com', password='instructor2', role='instructor',name='Paolo', surname='Verdi',  specialization='Calisthenics')
instructor_3 = Instructor(id=11, email='instructor3@gmail.com', password='instructor3', role='instructor', name='Chiara', surname='Gialli', specialization='Yoga')
zomba = Course(id=1, name='Zumba', places=10, gym=gold_gym.id, instructor=instructor.id)
calisthenics = Course(id=2, name='Calisthenics', places=12, gym=gold_gym.id, instructor=instructor_2.id)
yoga = Course(id=3, name='Yoga Relax', places=15, gym=gold_gym.id, instructor=instructor_3.id)

l = CourseScheduling(day_of_week='Monday', start_hour='19:00', end_hour='20:30', places=50, course=zomba.id)
m = CourseScheduling(day_of_week='Wednesday', start_hour='19:00', end_hour='20:30', places=50, course=zomba.id)
v = CourseScheduling(day_of_week='Friday', start_hour='19:00', end_hour='20:30', places=50, course=zomba.id)


l_c = CourseScheduling(day_of_week='Thursday', start_hour='20:00', end_hour='21:00', places=calisthenics.places, course=calisthenics.id)
m_c = CourseScheduling(day_of_week='Tuesday', start_hour='20:00', end_hour='21:00', places=calisthenics.places, course=calisthenics.id)

l_y = CourseScheduling(day_of_week='Saturday', start_hour='9:00', end_hour='10:00', places=yoga.places, course=yoga.id)
m_y = CourseScheduling(day_of_week='Wednesday', start_hour='10:00', end_hour='11:00', places=yoga.places, course=yoga.id)

db.session.add_all([
    instructor, zomba, l, m, v,
    instructor_2, calisthenics, l_c, m_c,
    instructor_3, yoga, l_y, m_y
])
###### END Courses ########

db.session.add_all([
    Member(id=3, email='alice@gmail.com', password='alice', role='user'),
    Member(id=4, email='daniele@gmail.com', password='daniele', role='user'),
    gold_gym,
    room_1,
    admin
])

db.create_all()

db.session.commit()

users = User.query.all ()
owners = Owner.query.all ()
instructors = Instructor.query.all ()

# for o in owners:
#     print (o)

print (metadata.tables.keys())

for u in owners:
    print (u)



