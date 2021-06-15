from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Gym, Users
from sqlalchemy import inspect

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metadata = MetaData()

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(50))
    role = db.Column(db.String(50))

    # def __init__(self, id, email, password, role):
    #     self.id = id
    #     self.email = email
    #     self.password = password
    #     self.role = role

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s', role='%s')>" % (self.id, self.email, self.password, self.role)


class Owner(Users, db.Model):
    __tablename__ = 'owner'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(50))
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    company_name = db.Column(db.String(100), nullable=False)

    # def __init__(self, id, role, name, surname, company_name):
    #     self.id = id
    #     self.role = role
    #     self.name = name
    #     self.surname = surname
    #     self.company_name = company_name

    def __repr__(self):
        return "<Owner(id='%s', email='%s', password='%s', name='%s', role='%s')>" % (self.id, self.email, self.password, self.name, self.role)

class Gym(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    zipCode = db.Column(db.String(100))
    country = db.Column(db.String(100))

    def __init__(self, id, name, address, city, zipCode, country):
        self.id = id
        self.name = name
        self.address = address
        self.city = city
        self.zipCode = zipCode
        self.country = country

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

    def __init__(self, id, name, places):
        self.id = id
        self.name = name
        self.places = places

    
gold_gym = Gym(id=1, name='Golden Gym', address='360 Hampton Dr', city='Venice', zipCode='90291', country='United States')

print(gold_gym.id)
room_1 = WeightRoom(id=1, name='Room 1', size='85', places='35', gym=gold_gym.id)

print(room_1.gym)

inst = inspect(Owner)
attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
print('-----------------------------------------')
print('Owner:')
print(attr_names)
print('-----------------------------------------')

db.session.add_all([
    Users(id=1, email='alice@gmail.com', password='alice', role='user'),
    Users(id=2, email='daniele@gmail.com', password='daniele', role='user'),
    Owner(id=3, email='admin@gmail.com', password='admin', role='owner', name='admin', surname='admin', company_name=''),
    gold_gym,
    room_1
])


db.create_all()

db.session.commit()

users = Users.query.all ()
owners = Owner.query.all ()

# for o in owners:
#     print (o)

print (metadata.tables.keys())

for u in users:
    print (u)
