from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Users

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

metadata = MetaData()

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    password = db.Column(db.String(50))  
    email = db.Column(db.String(100))

    def __init__(self, id, email, password):
        self.id = id
        self.password = password
        self.email = email

    def __repr__(self):
        return "<User(id='%s', email='%s', password='%s')>" % (self.id, self.email, self.password)

alice = Users(id=1, email='alice@gmail.com', password='alice')
daniele = Users(id=2, email='daniele@gmail.com', password='daniele')

db.create_all()

db.session.add(alice)
db.session.add(daniele)

db.session.commit()

users = Users.query.all ()


print(db.engine.table_names())

for u in users:
    print (u)
