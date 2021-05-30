from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response
from flask_login import login_required, current_user, login_manager, LoginManager, UserMixin, login_user, logout_user
from login import login_bp
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.register_blueprint(login_bp)
engine = create_engine('sqlite:///gymdatabase.db', echo = True)
metadata = MetaData()
Session = sessionmaker(bind=engine)       # creazione della factory
session = Session()

app.config['SECRET_KEY'] = 'ubersecret'

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, pwd, active=True):
        self.id = id 
        self.email = email 
        self.pwd = pwd
        self.active = active

def get_user_by_email(email): 
    conn = engine.connect()
    rs = conn.execute('SELECT * FROM users WHERE email = ?', email) 
    user = rs.fetchone()
    conn.close()
    return User(user.id, user.email, user.pwd)

@login_manager.user_loader # definisce la callback
def load_user(user_id):
    conn = engine.connect()
    rs = conn.execute('SELECT * FROM users WHERE id = ?', user_id) 
    user = rs.fetchone()
    conn.close()
    return User(user.id, user.email, user.pwd)


@app.route('/')
def home ():
    # current_user identifica l'utente attuale 
    # # utente anonimo prima dell'autenticazione 
    log(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('private')) 
    return render_template("login.html")

@app.route('/private')
@login_required # richiede autenticazione
def private ():
    conn = engine.connect()
    users = conn.execute('SELECT * FROM users')
    resp = make_response(render_template("private.html", users=users))
    conn.close()
    return resp

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login ():
    if request.method == 'POST':
        conn = engine.connect()
        rs = conn.execute('SELECT pwd FROM users WHERE email = ?', [request.form['user']]) 
        real_pwd = rs.fetchone()
        log(real_pwd)
        conn.close()
        if (real_pwd is not None):
            log('OK ' + request.form['pwd']+ '  ' +real_pwd['pwd'])
            if request.form['pwd'] == real_pwd['pwd']:
                user = get_user_by_email(request.form['user'])
                login_user(user)
                return redirect(url_for('private'))
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/test')
def test():
    u = request.args.get('user')
    #usafe
        #return "Welcome {}".format(u)
    #safe non viene interpretato come html
    return render_template('profile.html', user=u)


if __name__ == '__main__':
    app.run()

def log(message):
    print('Log message --> ', message)
