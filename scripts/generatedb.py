from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite supporta database transienti in RAM (echo attiva il logging)
engine = create_engine('sqlite:///gymdatabase.db', echo = True)
metadata = MetaData()
Base = declarative_base()                      # tabella = classe che eredita da Base
Session = sessionmaker(bind=engine) 
session = Session()

class User(Base):
    __tablename__ = 'users'                   # obbligatorio
    id = Column(Integer, primary_key=True)    # almeno un attributo deve fare parte della primary key
    email = Column(String)
    password = Column(String)

    
def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


metadata.create_all(engine)
conn = engine.connect()

session.add_all([User(email='alice@gmail.com', password='alice'),
                 User(email='dean@gmail.com', password='dean'),
                 User(email='test@gmail.com', password='test'),
                 User(email='daniele.berton2@gmail.com', password='flask')])

session.commit()
# ins = "INSERT INTO Users VALUES (?,?,?)"
# conn.execute(ins, ['1', 'alice@gmail.com', 'alice'])
# conn.execute(ins, ['2', 'dean@gmail.com', 'dean'])


user_list = conn.execute("SELECT * FROM Users")
for u in user_list:
    print ('User ----------> ',u)
