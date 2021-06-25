from flask import Blueprint, Response, json, jsonify, request, render_template, flash, redirect, url_for, send_file
from flask.templating import render_template
# from .open_cv import gen_frames
from .counter import compute_people
import time
from datetime import datetime
import random, json
from . import db
from .models import User, Customer
from flask_login import current_user

handlers = Blueprint('handlers', __name__)

def retrieve_customers(id, customers):
        total_customers = 0
        while True:
            if id:
                if len(customers) > total_customers:
                    status = [customer.status for customer in customers if customer.date.date() == datetime.now().date()]
                    date = [customer.date for customer in customers if customer.date.date() == datetime.now().date()]
                    json_data = json.dumps(
                        {'time': [x.time().strftime('%H:%M:%S') for x in date], 'status': status})
                    yield f"data:{json_data}\n\n"
                    total_customers = len(customers)
            time.sleep(3)

            
def get_customers(request):
    if request.method == 'POST':
        now = datetime.now()
        customer_status = request.form.get('status')
        
        customer = Customer(date=now, status=customer_status, user_id=current_user.id)
        db.session.add(customer)
        db.session.commit()

    customers = Customer.query.filter_by(user_id = current_user.id)
    return customers


@handlers.route("/video_feed")
@handlers.route("/video_feed/<video>")
def video_feed(video):
    if video != '0':
        video = 'website/static/videos/' + video
    else:
        video = int(video)
    return Response(compute_people(video, current_user, db), mimetype='multipart/x-mixed-replace; boundary=frame')


@handlers.route("/entry_data")
def entry_data():
    return Response(retrieve_customers(current_user.id, current_user.customers), mimetype='text/event-stream')


@handlers.route("add_entry", methods=['POST'])
def add_entry():
    if request.method == 'POST':
            # if request.form:
        now = datetime.now()
        customer_status = request.form.get('status')

        if customer_status and customer_status == "entry" or customer_status == "exit":
            customer = Customer(date=now, status=customer_status, user_id=current_user.id)
            db.session.add(customer)
            db.session.commit()
            flash("Customer Added Successfully", category='success')
            return redirect(url_for('views.home'))
        
    return redirect(url_for('views.home'))


@handlers.route("video", methods=['POST'])
def video():
    video = request.files["video"]
    if video.filename != '':
        video_name = "videos/video." + video.filename.split(".")[-1]
        video.save('website/static/' + video_name)
        return render_template("home.html", data={"user":current_user, 'video':video_name})
    return redirect(url_for("views.home"))