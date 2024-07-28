from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User, Admin


auth = Blueprint('auth', __name__,template_folder='templates',static_folder='static')

@auth.route('/')
def start():
    return render_template('start.html')

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        user = User.query.filter_by(email=email).first()
        remember = request.form.get('remember') == 'on'
        if user:
            if check_password_hash(user.password, pwd):
                flash('Logged in successfully!', category='success')
                if remember:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                return redirect(url_for('user_profile.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
            return render_template("login.html")

    return render_template("login.html", user=current_user)

@auth.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        firstname=request.form.get('firstname')
        pwd1=request.form.get('pwd1')
        pwd2=request.form.get('pwd2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Login using email', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstname) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif pwd1 != pwd2:
            flash('Passwords don\'t match.', category='error')
        elif len(pwd1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=firstname, password=generate_password_hash(pwd1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('user_profile.home'))

    return render_template('sign_up.html')

@auth.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form.get('username')
        pwd=request.form.get('pwd')
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if (admin.password==pwd):
                login_user(admin)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('admin_profile.admin_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
            return render_template("admin.html")

    return render_template("admin.html", user=current_user)
