from flask import Flask
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.register_blueprint(login_bp)

metadata = MetaData()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint('email', 'role', name='uniq_exec_email_role'),
    )
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))
    role = db.Column(db.String(50))
    #__mapper_args__ = {'polymorphic_on': email }

    def __init__(self, id, email, password, role):
        self.id = id
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s', role='%s')>" % (self.id, self.email, self.password, self.role)


class Owner(Users):
    __tablename__ = 'owner'
    __mapper_args__ = {'polymorphic_identity': 'users'}
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    company_name = db.Column(db.String(100), nullable=False)

    def __init__(self, id, email, password, role, name, surname, company_name):
        super().__init__(id, email, password, role)
        print('inside super: '+ name)
        self.name = name
        self.surname = surname
        self.company_name = company_name


    def __repr__(self):
        return "<Owner(id='%s', email='%s', password='%s', name='%s', role='%s')>" % (self.id, self.email, self.password, self.name, self.role)

class Member(Users, db.Model):
    __tablename__ = 'member'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __repr__(self):
        return "<Member(id='%s', email='%s', password='%s', name='%s', role='%s')>" % (self.id, self.email, self.password, self.name, self.role)

class Instructor(Users, db.Model):
    __tablename__ = 'instructor'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    specialization = db.Column(db.String(100))

    def __repr__(self):
        return "<Instructor(id='%s', email='%s', password='%s', role='%s')>" % (self.id, self.email, self.password, self.role)


class Gym(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    zipCode = db.Column(db.String(100))
    country = db.Column(db.String(100))
    owner = Column(Integer, ForeignKey('owner.id'))

    def __init__(self, id, name, address, city, zipCode, country, owner):
        self.id = id
        self.name = name
        self.address = address
        self.city = city
        self.zipCode = zipCode
        self.country = country
        self.owner = owner

class WeightRoom(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    size = db.Integer
    places = db.Integer
    gym = Column(Integer, ForeignKey('gym.id'))


    def __init__(self, id, name, size, places, gym):
        self.id = id
        self.name = name
        self.size = size
        self.places = places
        self.gym = gym

class Course(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        name = db.Column(db.String(100))
        places = db.Integer
        gym = Column(Integer, ForeignKey('gym.id'))

        def __init__(self, id, name, places, gym):
            self.id = id
            self.name = name
            self.places = places
            self.gym = gym

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column('id', db.Integer, primary_key = True)

class Slot(db.Model):
    __tablename__ = 'slot'
    id = db.Column('id', db.Integer, primary_key = True)
    day = db.Column(db.Integer)
    date = db.Column(db.Date)
    hourFrom = db.Column(db.String(100))
    hourTo = db.Column(db.String(100))


class Calendar:
    def __init__(self, day, month, day_name):
        self.day = day
        self.month = month
        self.day_name = day_name