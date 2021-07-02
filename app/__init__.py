import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, url_for, json, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from . import db
# from app.db import get_db

app = Flask(__name__)
# app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
# db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}'.format(
    user=os.getenv('POSTGRES_USER'),
    passwd=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    port=5432,
    table=os.getenv('POSTGRES_DB'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class UserModel(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"

# code by kOssi (https://stackoverflow.com/questions/21133976/flask-load-local-json)
# SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SITE_FOLDER = "static/data"

@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/profile/<name>')
def profile(name):
    json_url = os.path.join(SITE_ROOT, SITE_FOLDER, f"{name}.json")
    data = json.load(open(json_url))
    return render_template('profile.html', data=data)

@app.route('/health')
def health():
    return 'It Works!', 200

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return f"User {username} created successfully"
        else:
            return error, 418

    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200
        else:
            return error, 418
    return render_template('login.html', error='')