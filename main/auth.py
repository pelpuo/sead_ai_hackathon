from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# Login a user
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        print(user)

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully", category="success")
                login_user(user=user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("User does not exist. Please create an account", category="error")
    
    return render_template("login.html", data={"user":current_user})

# Logout a user
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# Register a new user
@auth.route("/register", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("fullname")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmpassword")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("User already exists", category="error")

        elif password != confirm_password:
            flash("passwords do not match", category='error')
        elif len(password) < 7:
            flash("password too short", category='error')
        elif len(email) < 1:
            flash("password too short", category='error')

        else:
            #add user to db
            hashed_password = generate_password_hash(password=password, method='sha256')
            new_user = User(email=email, full_name=full_name, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(user=new_user, remember=True)

            flash("Account created successfully", category='success')
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", data={"user":current_user})
