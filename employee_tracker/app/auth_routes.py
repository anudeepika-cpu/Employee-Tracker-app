from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user based on username
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            # Successfully logged in, direct to the appropriate dashboard based on the role
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))  # Admin dashboard
            else:
                return redirect(url_for('main.dashboard'))  # Employee dashboard
        flash("Invalid credentials", "error")
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        user = User(
            username=request.form['username'],
            password=hashed_pw,
            role='employee'  # force role to employee
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
