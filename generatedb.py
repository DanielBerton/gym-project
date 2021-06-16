from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Gym, Users
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import as_declarative, has_inherited_table, declared_attr


app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

metadata = MetaData()

db = SQLAlchemy(app)

class Users(db.Model):
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

admin = Owner(id=4, email='admin@gmail.com', 
              password='admin', role='owner', 
              name='admin', surname='admin', 
              company_name='')
print(admin.id)

gold_gym = Gym(id=1, name='Golden Gym', address='360 Hampton Dr', city='Venice', zipCode='90291', country='United States', owner=admin.id)

room_1 = WeightRoom(id=1, name='Room 1', size='85', places='35', gym=gold_gym.id)





# inst = inspect(Owner)
# attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
# print('-----------------------------------------')
# print('Owner:')
# print(attr_names)
# print('-----------------------------------------')

db.session.add_all([
    Member(id=1, email='alice@gmail.com', password='alice', role='user'),
    Member(id=2, email='daniele@gmail.com', password='daniele', role='user'),
    Instructor(id=3, email='daniele2@gmail.com', password='daniele', role='intructor'),
    gold_gym,
    room_1,
    admin
])


db.create_all()

db.session.commit()

users = Users.query.all ()
owners = Owner.query.all ()
instructors = Instructor.query.all ()

# for o in owners:
#     print (o)

print (metadata.tables.keys())

for u in owners:
    print (u)

# for u in users:
#     print (u)

