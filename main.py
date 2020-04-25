import os
from datetime import timedelta

from flask import Flask, render_template, redirect, url_for, flash, session, request, g
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField
from wtforms.validators import InputRequired,Email,Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user

app=Flask(__name__)
app.config['SECRET_KEY']='Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Helsinki@localhost:5432/users'
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


class Database(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return Database.query.get(int(user_id))

class LoginForm(FlaskForm):
    username=StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])
    remember=BooleanField('remember me')


class RegisterForm(FlaskForm):

    email=StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
    username = StringField('username', validators=[ InputRequired(), Length(min=4, max=15) ])
    password = PasswordField('password', validators=[ InputRequired(), Length(min=8, max=80) ])

@app.route('/')
def index():
    return render_template('test.html')

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


@app.route('/dashboard')
@login_required
def dashboard():
    if g.user:
        # return render_template('dashboard.html',name=current_user.username)
        return render_template('dashboard.html',user=session['user'])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


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

if __name__=="__main__":
    @app.context_processor
    def override_url_for():
        return dict(url_for=dated_url_for)


    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path,
                                         endpoint, filename)
                values[ 'q' ] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)
    app.run(debug=True)
