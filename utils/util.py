
from models import *
from .log import log
from flask import Flask
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, load_only
from contextlib import contextmanager


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})

metadata = MetaData()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine)
session = Session()

db = SQLAlchemy(app)
from contextlib import contextmanager


@contextmanager
def get_session():
    log('------------------- start transaction -------------------')
    session = db.session

    try:
        yield session
    except:
        session.rollback()
        raise
    else:
        session.commit()
