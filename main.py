import os
from datetime import timedelta

import click
from flask import Flask, render_template, redirect, url_for, flash, session, request, g
from flask.cli import with_appcontext
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField
from wtforms.validators import InputRequired,Email,Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user

# Created a Flask instance

app=Flask(__name__)

# Here below code states that based on the environment(Production or environment) it will connect to that particular database

ENV='prod'
if ENV == 'dev':
    app.debug = True
    app.config[ 'SQLALCHEMY_DATABASE_URI' ] = 'postgresql://postgres:Helsinki@localhost:5432/users'


else:
    app.debug = False
    app.config[ 'SQLALCHEMY_DATABASE_URI' ]='postgres://jfrjcnkutalcef:72270166de3c5782bf3abdfb677f039558f1c4d21d53b6758c51b8f96424ed49@ec2-3-223-21-106.compute-1.amazonaws.com:5432/d3v7gj3hjsf4k8'

app.config[ 'SECRET_KEY' ] = 'Thisissupposedtobesecret!'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
# login_mgr = LoginManager(app)
# login_mgr.login_view = 'login'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"

# Here below is the class created for the structure of our table in the database

class Database(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(80))

    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password

@login_manager.user_loader
def load_user(user_id):
    return Database.query.get(int(user_id))

# Method for login form which takes the inputs from the user when user submits the login form

class LoginForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])
    remember=BooleanField('remember me')


# Method for registration form which takes the inputs from the user when user submits the registration form


class RegisterForm(FlaskForm):

    email=StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
    username = StringField('username', validators=[ InputRequired(), Length(min=4, max=15) ])
    password = PasswordField('password', validators=[ InputRequired(), Length(min=8, max=80) ])

# Below are the routes created so on typing particular route it navigates to that page

# Route for Home page
@app.route('/')
def index():
    return render_template('test.html')

# Route for the login page

@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Database.query.filter_by(username=form.username.data).first()
        if user:
            session.pop('user', None)

            if check_password_hash(user.password,form.password.data):
                session['user']=request.form['username']
                login_user(user,remember=form.remember.data)
                flash('You were successfully logged in')

                return redirect(url_for('dashboard'))

        else:
            return render_template('test.html')

        # flash('Invalid username or password')
        # return '<h1>'+form.username.data+" "+form.password.data + '</h1>'

    return render_template('login.html',form=form)

# Route for the signup page

@app.route('/signup',methods=['GET','POST'])
def signup():
    form=RegisterForm()

    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data,method='sha256')
        new_user=Database(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('You were successfully signed up')
        # return '<h2> Successfully signed up</h2>'
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

# Route for the dashboard

@app.route('/dashboard')
@login_required
def dashboard():
    if g.user:
        # return render_template('dashboard.html',name=current_user.username)
        return render_template('dashboard.html',user=session['user'])

# Logout route

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Method for creating tables that as specified by the Database class above
@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user=session['user']

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route('/dropsession')
def dropsession():
    session.pop('user',None)
    return reversed('login.html')

# Program starts from here

if __name__=="__main__":

    app.run()
