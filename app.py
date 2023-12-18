import os
from flask import Flask, session, render_template, redirect, request, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required, calculate_odds, get_results, get_live
from werkzeug.security import check_password_hash, generate_password_hash
from models import *
from datetime import datetime, timedelta

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
history_list = []


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)
    render_template("layout.html", user_balance=user_balance)
    bets = Bet.query.filter_by(user_id=user.id).all()
    current_date_time = datetime.now()
    for bet in bets:
        bet_time_composed_str = (f"{bet.date} {bet.time}")
        bet_time_composed_time = datetime.strptime(bet_time_composed_str, "%Y-%m-%d %H:%M:%S")
        bet_time_composed_finished = bet_time_composed_time + timedelta(minutes=240)
        
        if bet_time_composed_finished > current_date_time > bet_time_composed_time:
            print("bet zou in live moeten zijn")
            results = get_live(bet.competition_id)
        else:
            print("bet zou in history moeten staan")
            results = get_results(bet.competition_id)
        if bet.match_id in results:
            if bet.winner == results[bet.match_id]['outcome']:
                user.balance += bet.possible_payout
                competition_id= bet.competition_id
                match_id= bet.match_id
                predicted_winner= bet.winner
                predicted_winner_team= bet.winner_team
                status= 'Won'
                actual_winner = results[bet.match_id]['outcome']
                odds= bet.odds
                stake= bet.stake
                balance_change= f'+ {(int(bet.possible_payout))}' 
                user_id=user.id
                date= bet.date
                time= bet.time
                team1= bet.team1
                team2= bet.team2
                history = Bet_history(match_id = match_id, status=status, competition_id=competition_id, predicted_winner=predicted_winner, predicted_winner_team=predicted_winner_team, odds=odds, stake=stake, balance_change=balance_change, user_id=user_id, team1=team1, date=date, team2=team2, time=time)
                db.session.add(history)
                db.session.commit()
            else:
                competition_id= bet.competition_id
                match_id= bet.match_id
                predicted_winner= bet.winner
                predicted_winner_team= bet.winner_team
                status= 'Lost'
                actual_winner = results[bet.match_id]['outcome']
                odds= bet.odds
                stake= bet.stake
                balance_change= f'- {(int(bet.stake))}' 
                user_id=user.id
                date= bet.date
                time= bet.time
                team1= bet.team1
                team2= bet.team2
                history = Bet_history(match_id = match_id, status=status, competition_id=competition_id, predicted_winner=predicted_winner, actual_winner=actual_winner, predicted_winner_team=predicted_winner_team, odds=odds, stake=stake, balance_change=balance_change, user_id=user_id, team1=team1, date=date, team2=team2, time=time)
                db.session.add(history)
                db.session.commit()
            db.session.delete(bet)
            db.session.commit()
        else:
            print('niet gevonden')
    else:
        print("Geen resultaten opgehaald")
    
    global live_score_id
    global match_info

    if request.method == "POST":          
        competition_name = request.form.get("competition")
        if not competition_name:
            return render_template("index.html")
        if competition_name:
            competition = Competition.query.filter(Competition.name.ilike(f"%{competition_name}%")).first()
            if competition:
                live_score_id = competition.live_score_id
                match_info = calculate_odds(live_score_id)
                return render_template("index.html", competition=competition.name, match_info=match_info, username=user.username, user_balance=user_balance)
            return render_template("index.html", user_balance=user_balance)
        else:
           return render_template("index.html", user_balance=user_balance)     
    else:
        live_score_id = 196
        match_info = calculate_odds(live_score_id)
        return render_template("index.html", competition='Eredivisie', match_info=match_info, username=user.username, user_balance=user_balance)

    
@app.route("/wedstrijdformulier/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier(index):
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    user_balance = int(user.balance)
    if request.method == "POST":
        if request.form.get('team1'):
            odds = request.form.get('team1')
            winner_string = f"Winst voor {match_info[index]['team1']}"
            winner = '1'
            winner_team = match_info[index]['team1']
        elif request.form.get('draw'):
            odds = request.form.get('draw')
            winner_string = "Gelijkspel"
            winner = 'X'
            winner_team = 'gelijkspel'
        elif request.form.get('team2'):
            odds = request.form.get('team2')
            winner_string = f"Winst voor {match_info[index]['team2']}"
            winner = '2'
            winner_team = match_info[index]['team2']
        else:
            odds = None
            winner_string = None
            winner = None
        return render_template("wedstrijdformulier.html", index=index, match_info=match_info[index], odds=odds, winner_team=winner_team, winner_string=winner_string, winner=winner, username=user.username, user_balance = user_balance)
    
@app.route("/wedstrijdformulier/bet/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier2(index):
    if request.method == "POST":
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        bets = Bet.query.filter_by(user_id=user.id).all()
        match_id = request.form.get('match_id')
        for bet in bets:
            if bet.match_id == match_id:
                flash("Je hebt al een bet gezet op deze wedstrijd, je kunt niet meerdere bets zetten op één wedstrijd!", "warning")
                return redirect("/")
        winner = request.form.get('winner')
        winner_team = request.form.get('winner_team')
        team1 = request.form.get('team1')
        team2 = request.form.get('team2')
        time = request.form.get('time')
        date = request.form.get('date')
        odds = request.form.get('odds')
        stake = request.form.get('inzet')
        potential_winning = request.form.get('potential_winning')
        user_id = session["user_id"]
        
        bet = Bet(match_id = match_id, competition_id=live_score_id, winner=winner, winner_team=winner_team, odds=odds, stake=stake, possible_payout=potential_winning, user_id=user_id, team1=team1, date=date, team2=team2, time=time)
        db.session.add(bet)
        db.session.commit()

        user = User.query.filter_by(id=user_id).first()
        user.balance = int(user.balance) - int(stake)
        db.session.commit()
        return redirect("/")


@app.route("/matches", methods=["GET"])
@login_required
def matches():
    return render_template("matches.html")
    
@app.route("/bets", methods=["GET"])
@login_required
def bets():
    # print(f"match_info = {match_info}")
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    bets_dict = {}
    bets = Bet.query.filter_by(user_id=user.id).all()

    for index, bet in enumerate(bets):
        competition = Competition.query.filter_by(live_score_id=bet.competition_id).first()
        competition = competition.name
        match_id = bet.match_id
        winner = bet.winner
        winner_team = bet.winner_team
        odds = bet.odds
        stake = bet.stake
        possible_payout = bet.possible_payout
        date = bet.date
        time = bet.time
        team1 = bet.team1
        team2 = bet.team2
        bets_dict[index] = {'competition': competition, 'match_id': match_id, 'winner': winner, 'winner_team': winner_team, 'odds': odds, 'stake': stake, 'possible_payout': possible_payout, 'date': date, 'time': time, 'team1': team1, 'team2': team2}
    return render_template("bets.html", username=user.username, user_balance=user_balance, bets=bets_dict)

@app.route("/ranking", methods=["GET"])
@login_required
def ranking():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    all_users = User.query.order_by(desc(User.balance)).all()
    user_dict = {}
    for index, user in enumerate(all_users):
        username = user.username
        user_balance_dict = user.balance
        print(user_balance_dict)
        user_dict[index] = {'username': username, 'user_balance': user_balance_dict}
    user = User.query.filter_by(id=user_id).first()
    return render_template("ranking.html", username=user.username, user_balance=user_balance, users=user_dict)

@app.route("/history", methods=["GET"])
@login_required
def history():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    bet_history_dict = {}
    bet_history = Bet_history.query.filter_by(user_id=user.id).all()

    for index, bet in enumerate(bet_history):
        competition = Competition.query.filter_by(live_score_id=bet.competition_id).first()
        competition = competition.name
        match_id = bet.match_id
        predicted_winner = bet.predicted_winner
        predicted_winner_team = bet.predicted_winner_team
        actual_winner = bet.actual_winner
        status = bet.status
        odds = bet.odds
        stake = bet.stake
        balance_change = bet.balance_change
        date = bet.date
        time = bet.time
        team1 = bet.team1
        team2 = bet.team2
        bet_history_dict[index] = {'competition': competition, 'status': status, 'match_id': match_id, 'predicted_winner': predicted_winner, 'actual_winner': actual_winner, 'predicted_winner_team': predicted_winner_team, 'odds': odds, 'stake': stake, 'balance_change': balance_change, 'date': date, 'time': time, 'team1': team1, 'team2': team2}
        print(bet_history_dict)
    
    return render_template("history.html", username=user.username, user_balance=user_balance, bet_history=bet_history_dict)

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

