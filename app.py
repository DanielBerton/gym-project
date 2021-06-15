from models import *
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join
from sqlalchemy.sql import select

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = create_engine('sqlite:///database.db', echo=True)

app.register_blueprint(login_bp)

metadata = MetaData()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)

Session = sessionmaker(bind = engine)
session = Session()

db = SQLAlchemy(app)

def get_user_by_email(email):
    log('[get_user_by_email] executed', '')
    user = Users.query.filter_by (email=email).first()
    log('[get_user_by_email] user: ', user)
    return user

@login_manager.user_loader # definisce la callback
def load_user(user_id):

    log('[load_user] user_id: ', user_id)
    user = Users.query.filter_by(id=user_id).first()
    log('[load_user] Logged user: ',user)
    return user


@app.route('/')
def home ():
    log('[home] executed')
    # current_user identifica l'utente attuale 
    # # utente anonimo prima dell'autenticazione 
    log(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('private')) 
    return render_template("login.html")

@app.route('/private')
@login_required # richiede autenticazione
def private ():
    log('[private] executed')
    users = Users.query.all()
    log('[private] users ', users)
    resp = make_response(render_template("private.html", users=users))

    gyms = session.query(Gym, WeightRoom).filter(Gym.id==WeightRoom.gym).all()

    golden = session.query(Gym).join(WeightRoom).filter(Gym.id == WeightRoom.gym).first()

    # gyms = Gym.query.all()
    log(golden)
    return resp

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    log('[logout] executed', '')
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login ():
    log('[login] executed')
    if request.method == 'POST':

        email = request.form['user']

        user = Users.query.filter_by(email=email).first()

        log('[login] user: ',  user)
        if (user and user.password is not None):
            log('[login]', 'OK ' + request.form['password']+ '  ' +user.password)
            if request.form['password'] == user.password:
                users = get_user_by_email(request.form['user'])
                login_user(users)
                return redirect(url_for('private'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/test')
def test():
    u = request.args.get('Users')
    #usafe
        #return "Welcome {}".format(u)
    #safe non viene interpretato come html
    return render_template('profile.html', Users=u)


if __name__ == '__main__':
    app.run()

# Logger method
# param message is optional
def log(method, message=''):
    print('---------------------------------')
    print(method, message)
    print('---------------------------------')
