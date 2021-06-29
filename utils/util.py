
from models import *
from .log import log
from flask import Flask
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, load_only
from contextlib import contextmanager
from config import SECRET_KEY


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True, connect_args={'check_same_thread': False})
# echo shows query and executions, set true just for development 

metadata = MetaData()

app.config['SECRET_KEY'] = SECRET_KEY

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
        log('COMMIT ==========================================================================================')

        session.commit()
