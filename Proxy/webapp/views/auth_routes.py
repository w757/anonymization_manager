from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from common.models import User
from common.extensions import db, login_manager
from forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('swagger.index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already taken.', 'danger')
            return render_template('register.html', form=form)

        user = User(username=form.username.data, role='admin')  # lub 'user'
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
