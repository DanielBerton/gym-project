import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///gymdatabase.db', echo=True)

Base = declarative_base()                      # tabella = classe che eredita da Base
Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()

class User(Base):
    __tablename__ = 'users'                   # obbligatorio

    id = Column(Integer, primary_key=True)    # almeno un attributo deve fare parte della primary key
    email = Column(String)
    pwd = Column(String)
    
User.__table__
Base.metadata.create_all(engine)

# questo metodo è opzionale, serve solo per pretty printing
def __repr__(self):
    return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)

session.add_all([User(email='alice@gmail.com', pwd='alice'),
                 User(email='dean@gmail.com', pwd='dean'),
                 User(email='test@gmail.com', pwd='test'),
                 User(email='daniele.berton2@gmail.com', pwd='flask')])

session.commit()