from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, default=10000)

class Competition(db.Model):
    __tablename__ = "competition"
    id = db.Column(db.Integer, primary_key=True)
    live_score_id = db.Column(db.Integer)
    name = db.Column(db.String(255))

class Bet(db.Model):
    __tablename__ = "bet"
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer)
    match_id = db.Column(db.String(255))
    winner = db.Column(db.String(255))
    winner_team = db.Column(db.String(255))
    odds = db.Column(db.Float)
    stake = db.Column(db.Float)
    possible_payout = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.String(255))
    date = db.Column(db.String(255))
    team1 = db.Column(db.String(255))
    team2 = db.Column(db.String(255))

class Bet_history(db.Model):
    __tablename__ = "bet_history"
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer)
    match_id = db.Column(db.String(255))
    predicted_winner = db.Column(db.String(255))
    actual_winner = db.Column(db.String(255))
    predicted_winner_team = db.Column(db.String(255))
    status = db.Column(db.String(255))
    odds = db.Column(db.Float)
    stake = db.Column(db.Float)
    balance_change = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.String(255))
    date = db.Column(db.String(255))
    team1 = db.Column(db.String(255))
    team2 = db.Column(db.String(255))




