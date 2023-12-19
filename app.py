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

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

match_info = {}
history_list = []

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Get username and user balance for navbar
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)
    render_template("layout.html", user_balance=user_balance)
    
    # Query all current bets
    bets = Bet.query.filter_by(user_id=user.id).all()
    
    # Check current time
    current_date_time = datetime.now()
    
    for bet in bets:
        # Compare current time to the time the match of corresponding bet is finished
        bet_time_composed_str = (f"{bet.date} {bet.time}")
        bet_time_composed_time = datetime.strptime(bet_time_composed_str, "%Y-%m-%d %H:%M:%S")
        bet_time_composed_finished = bet_time_composed_time + timedelta(minutes=240)
        
        # Check per bet whether the game has already started
        if current_date_time > bet_time_composed_time:
            # Request live-data if match has finished within 4 hours of current time
            if bet_time_composed_finished > current_date_time > bet_time_composed_time:
                results = get_live(bet.competition_id)
            # Request history data if match has finished more than 4 hours ago
            else:
                print("bet zou in history moeten staan")
                results = get_results(bet.competition_id)
        # if the game has not yet started no requests are made
        else:
            results = None

        # Check whether match can be found in the data requested by API
        if results != None and bet.match_id in results:
            # If bet is won, create Bet_history object where status is won and balance change is positive
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
                history = Bet_history(match_id = match_id, 
                                      status=status, 
                                      competition_id=competition_id, 
                                      predicted_winner=predicted_winner, 
                                      predicted_winner_team=predicted_winner_team, 
                                      odds=odds, 
                                      stake=stake, 
                                      balance_change=balance_change, 
                                      user_id=user_id, 
                                      team1=team1, 
                                      date=date, 
                                      team2=team2, 
                                      time=time)
                db.session.add(history)
                db.session.commit()
            # If bet is lost, create Bet_history object where status is lost and balance change is unchanged
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
                history = Bet_history(match_id = match_id, 
                                      status=status, 
                                      competition_id=competition_id, 
                                      predicted_winner=predicted_winner, 
                                      actual_winner=actual_winner, 
                                      predicted_winner_team=predicted_winner_team, 
                                      odds=odds, 
                                      stake=stake, 
                                      balance_change=balance_change, 
                                      user_id=user_id, 
                                      team1=team1, 
                                      date=date, 
                                      team2=team2, 
                                      time=time)
                
                db.session.add(history)
                db.session.commit()
            # Delete bet object
            db.session.delete(bet)
            db.session.commit()
        else:
            pass
    else:
        pass
    
    # Create global variable for competition id and dictionary for competition data
    global live_score_id
    global match_info

    if request.method == "POST":
        # Find competition         
        competition_name = request.form.get("competition")
        if not competition_name:
            return render_template("index.html")
        if competition_name:
            competition = Competition.query.filter(Competition.name.ilike(f"%{competition_name}%")).first()
            if competition:
                # Convert competition name to competition id
                live_score_id = competition.live_score_id
                # request data based on competition id
                match_info = calculate_odds(live_score_id)
                return render_template("index.html", competition=competition.name, 
                                                    match_info=match_info, 
                                                    username=user.username, 
                                                    user_balance=user_balance)
            
            return render_template("index.html", user_balance=user_balance)
        else:
           return render_template("index.html", user_balance=user_balance)     
    else:
        # Matches from dutch footbal competition are shown by default
        live_score_id = 196
        match_info = calculate_odds(live_score_id)
        return render_template("index.html", competition='Eredivisie', 
                               match_info=match_info, username=user.username, 
                               user_balance=user_balance)

    
@app.route("/wedstrijdformulier/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier(index):
    # Get username and user balance for navbar
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    user_balance = int(user.balance)

    # Set variables based on the button that was clicked
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
        return render_template("wedstrijdformulier.html", index=index, 
                                                        match_info=match_info[index], 
                                                        odds=odds, 
                                                        winner_team=winner_team, 
                                                        winner_string=winner_string, 
                                                        winner=winner, 
                                                        username=user.username, 
                                                        user_balance = user_balance)
    
@app.route("/wedstrijdformulier/bet/<int:index>", methods=["GET", "POST"])
@login_required
def wedstrijdformulier2(index):
    # Create a bet object for the chosen bet
    if request.method == "POST":
        user_id = session["user_id"]
        user = User.query.filter_by(id=user_id).first()
        bets = Bet.query.filter_by(user_id=user.id).all()
        # Set variables for betting object
        match_id = request.form.get('match_id')
        for bet in bets:
            # Make sure it is not possible to bet on the same match twice
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
        #Create bet object
        bet = Bet(match_id = match_id, 
                  competition_id=live_score_id, 
                  winner=winner, winner_team=winner_team, 
                  odds=odds, 
                  stake=stake, 
                  possible_payout=potential_winning, 
                  user_id=user_id, 
                  team1=team1, 
                  date=date, 
                  team2=team2, 
                  time=time)
        
        db.session.add(bet)
        db.session.commit()
        # Subtract stake from user balance
        user = User.query.filter_by(id=user_id).first()
        user.balance = int(user.balance) - int(stake)
        db.session.commit()
        return redirect("/")


@app.route("/matches", methods=["GET"])
@login_required
def matches():
    # Matches has same functionality as the home page
    return redirect("/")


@app.route("/bets", methods=["GET"])
@login_required
def bets():
    # Get username and user balance for navbar
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    # Create empty bets dictionary
    bets_dict = {}
    bets = Bet.query.filter_by(user_id=user.id).all()
    # Set variables for all bets that have been made
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
        # Save all varibales in a dictionary to send that the the html page
        bets_dict[index] = {'competition': competition, 
                            'match_id': match_id, 
                            'winner': winner, 
                            'winner_team': winner_team, 
                            'odds': odds, 
                            'stake': stake, 
                            'possible_payout': possible_payout, 
                            'date': date, 
                            'time': time, 
                            'team1': team1, 
                            'team2': team2}
    return render_template("bets.html", username=user.username, user_balance=user_balance, bets=bets_dict)

@app.route("/ranking", methods=["GET"])
@login_required
def ranking():
    # Get username and user balance for navbar
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    # Query all users and order by balance
    all_users = User.query.order_by(desc(User.balance)).all()
    #Create empty user dictionary
    user_dict = {}
    rank = 1
    # Set variables for all users that have an account
    for index, user in enumerate(all_users):
        rank = rank
        username = user.username
        user_balance_dict = user.balance
        # Save all varibales in a dictionary to send that the the html page
        user_dict[index] = {'rank': rank, 
                            'username': username, 
                            'user_balance': user_balance_dict}
        rank += 1
    user = User.query.filter_by(id=user_id).first()
    return render_template("ranking.html", username=user.username, user_balance=user_balance, users=user_dict)

@app.route("/history", methods=["GET"])
@login_required
def history():
    # Get username and user balance for navbar
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    db.session.commit()
    user_balance = int(user.balance)

    # Create empty history dictionary
    bet_history_dict = {}
    bet_history = Bet_history.query.filter_by(user_id=user.id).all()

    # Set variables for all bets in the bet history
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
        # Save all varibales in a dictionary to send that the the html page
        bet_history_dict[index] = {'competition': competition, 
                                   'status': status, 
                                   'match_id': match_id, 
                                   'predicted_winner': predicted_winner, 
                                   'actual_winner': actual_winner, 
                                   'predicted_winner_team': predicted_winner_team, 
                                   'odds': odds, 
                                   'stake': stake, 
                                   'balance_change': balance_change, 
                                   'date': date, 
                                   'time': time, 
                                   'team1': team1, 
                                   'team2': team2}
    
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
        user = User.query.filter_by(username=username).first()
        user_hash = user.hash
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
        if User.query.filter_by(username=username).first():
            return "Apology, 400: username already exists"
        
        # Give error when the forms have not been submitted in the right way
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

