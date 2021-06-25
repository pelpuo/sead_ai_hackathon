from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .open_cv import list_ports

views = Blueprint('views', __name__)

@views.route("/")
@login_required
def home():
    # working_ports = list_ports()
    # working_ports = [0]
    return render_template("home.html", data={"user":current_user})

@views.route("/history")
@login_required
def history():
    dates = [customer.date.strftime('%d-%m-%Y') for customer in current_user.customers]
    dates = set(dates)
    dates = list(dates)
    dates.sort()
    dates.reverse()
    print(dates)
    return render_template("history.html", data={"user":current_user, 'dates': dates})

@views.route("/history/<date>")
@login_required
def date_history(date): 
    status = [customer.status for customer in current_user.customers if customer.date.strftime('%d-%m-%Y') == date]
    time = [customer.date.time().strftime('%H:%M:%S') for customer in current_user.customers if customer.date.strftime('%d-%m-%Y') == date]
    
    return jsonify({'status':status, 'time':time})

@views.route("/allhistory")
@login_required
def all_history(): 
    dates = [customer.date.strftime('%d-%m-%Y') for customer in current_user.customers]
    dates = set(dates)
    dates = list(dates)
    dates.sort()
    
    tallies = []
    for date in dates:
        tally = 0
        for customer in current_user.customers:
            if customer.date.strftime('%d-%m-%Y') == date:
                if customer.status == "entry":
                    tally += 1
                else:
                    tally -= 1
        tallies.append(tally)
    print(tallies)
    return jsonify({'dates':dates, 'tallies':tallies})