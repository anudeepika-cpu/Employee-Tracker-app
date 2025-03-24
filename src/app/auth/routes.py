from flask import render_template, redirect, url_for, flash, Blueprint
from app import db, bcrypt
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.models import User
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)  # Fix applied

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Login failed. Please check your email and password.", "danger")

    return render_template("auth/login.html", form=form)  # Ensure this path is correct

@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
