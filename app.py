import os

from flask import Flask, session, render_template, redirect, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models import *
from fixtures import calculate_odds

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

match_info = {}

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    user_balance = int(user.balance)
    if request.method == "POST":    
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        user_balance = int(user.balance)
        print(f"user balance in / = {user_balance}")
        render_template("layout.html", user_balance=user_balance)
        
        competition_name = request.form.get("competition")

        if not competition_name:
            return render_template("index.html")
        
        if competition_name:
            competition = Competition.query.filter(Competition.name.ilike(f"%{competition_name}%")).first()
            if competition:
                live_score_id = competition.live_score_id
                global match_info
                match_info = calculate_odds(live_score_id)
                return render_template("index.html", competition=competition.name, match_info=match_info, user_balance=user_balance)
            
            return render_template("index.html")
        else:
           return render_template("index.html")     
    else:   
        return render_template("index.html", user_balance=user_balance)
    
@app.route("/wedstrijdformulier/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier(index):
    if request.method == "POST":
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        user_balance = int(user.balance)
        render_template("layout.html", user_balance=user_balance)

        if request.form.get('team1'):
            odds = request.form.get('team1')
            winner_string = f"Winst voor {match_info[index]['team1']}"
            winner = '1'
        elif request.form.get('draw'):
            odds = request.form.get('draw')
            winner_string = "Gelijkspel"
            winner = 'X'
        elif request.form.get('team2'):
            odds = request.form.get('team2')
            winner_string = f"Winst voor {match_info[index]['team2']}"
            winner = '2'
        else:
            odds = None
            winner_string = None
            winner = None
        return render_template("wedstrijdformulier.html", index=index, match_info=match_info[index], odds=odds, winner_string=winner_string, winner=winner)

@app.route("/wedstrijdformulier/bet/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier2(index):
    if request.method == "POST":
        match_id = request.form.get('match_id')
        print(match_id)
        winner = request.form.get('winner')
        print(winner)
        odds = request.form.get('odds')
        print(odds)
        stake = request.form.get('inzet')
        print(stake)
        potential_winning = request.form.get('potential_winning')
        print(f"potential winning = {potential_winning}")
        user_id = session["user_id"]
        print(user_id)

        bet = Bet(match_id = match_id, winner=winner, odds=odds, stake=stake, possible_payout=potential_winning, user_id=user_id)
        db.session.add(bet)
        db.session.commit()

        user = User.query.filter_by(id=user_id).first()
        user.balance = int(user.balance) - int(stake)

        db.session.commit()
        print(user.balance)
        return redirect("/")

    

@app.route("/matches", methods=["GET"])
@login_required
def matches():
    return render_template("matches.html")
    
@app.route("/bets", methods=["GET"])
@login_required
def bets():
    return render_template("bets.html")

@app.route("/ranking", methods=["GET"])
@login_required
def ranking():
    return render_template("ranking.html")

@app.route("/history", methods=["GET"])
@login_required
def history():
    return render_template("history.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        # print(password)
        if not username:
            return "Apology, 400: must provide username"
        elif not password:
            return "Apology, 400: must provide password"
        
        hash = generate_password_hash(password)
        # print(hash)
        user = User.query.filter_by(username=username).first()
        # print(user)
        user_hash = user.hash
        # print(user_hash)
        user_id = user.id
        
        if User.query.filter_by(username=username).first():
            if check_password_hash(user_hash, password):
                session["user_id"] = user_id
                return redirect("/")
            else:
                return "Apology: incorrect username, password combination, 403"
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmed_password = request.form.get("confirmation")
        
        # print(User.query.filter_by(username=username).first())
        if User.query.filter_by(username=username).first():
            return "Apology, 400: username already exists"
        
        if not username:
            return "Apology, 400: must provide username"
        elif not password:
            return "Apology, 400: must provide password"
        elif not confirmed_password:
            return "Apology, 400: must confirm password"
        if password != confirmed_password:
            return "Apology, 400: passwords are not the same" 
        
        hash = generate_password_hash(password)
        

        user = User(username=username, hash=hash)
        db.session.add(user)
        db.session.commit()
        
        return render_template("login.html")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

