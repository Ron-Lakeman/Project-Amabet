import requests
from models import *
import requests
from flask import redirect, session
from functools import wraps

from flask import Flask, session, render_template, redirect, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from models import *
from datetime import datetime

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_ranking(id):
    res = requests.get(f" https://livescore-api.com/api-client/leagues/table.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    ranking_data = res.json()
    ranking = ranking_data['data']['table']
    table_info = {}

    for index, table in enumerate(ranking):
        rank = table['rank']
        team_id = table['team_id']
        team = table['name']
        matches = table['matches']
        points = table['points']
        goals_scored = table['goals_scored']
        goals_conceded = table['goals_conceded']
        won = table['won']
        draw = table['drawn']
        lost = table['lost']
        table_info[index] = {'rank': rank, 'team_id': team_id, 'team': team, 'matches': matches, 'points': points, 'goals_conceded': goals_conceded, 'goals_scored': goals_scored, 'won': won, 'draw': draw, 'lost': lost}

    return(table_info)

def get_fixtures(id):
    
    match_info = {}
    res2 = requests.get(f"https://livescore-api.com/api-client/fixtures/matches.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    fixtures_data = res2.json()
    fixtures = fixtures_data['data']['fixtures']

    for index, match in enumerate(fixtures):
        match_id = match['id']
        home_id = match['home_id']
        team1 = match['home_name']
        away_id = match['away_id']
        team2 = match['away_name']
        date = match['date']
        location = match['location']
        time = match['time']
        match_id = f"{home_id}-{away_id}-{date}"
        match_info[index] = {'match_id': match_id, 'home_id': home_id, 'team1': team1, 'away_id': away_id, 'team2': team2, 'date': date, 'location': location, 'time': time}
    return(match_info)
        

def get_fixtures_and_rank(id):
    ranking_data = get_ranking(id)
    fixtures_data = get_fixtures(id)
    for rank_key, x in ranking_data.items():
        for match_key, y in fixtures_data.items():
            if str(fixtures_data[match_key]['home_id']) == str(ranking_data[rank_key]['team_id']):
                fixtures_data[match_key]['team1_ranking'] = ranking_data[rank_key]['rank']
                fixtures_data[match_key]['team1_points'] = ranking_data[rank_key]['points']
                fixtures_data[match_key]['team1_matches'] = ranking_data[rank_key]['matches']
            elif str(ranking_data[rank_key]['team_id']) == str(fixtures_data[match_key]['away_id']):
                fixtures_data[match_key]['team2_ranking'] = ranking_data[rank_key]['rank']
                fixtures_data[match_key]['team2_points'] = ranking_data[rank_key]['points']
                fixtures_data[match_key]['team2_matches'] = ranking_data[rank_key]['matches']
    return fixtures_data
            
def calculate_odds(id):
    fixtures_data = get_fixtures_and_rank(id)
    for rank_key, x in fixtures_data.items():
        for match_key, y in fixtures_data.items():
            team1_points = int(fixtures_data[match_key]['team1_points'])
            team2_points = int(fixtures_data[match_key]['team2_points'])
            
            probability_team1_win = team1_points / (team1_points + team2_points)
            probability_team2_win = team2_points / (team1_points + team2_points)
            
            max_points = int(fixtures_data[rank_key]['team1_matches']) * 3
            probability_draw = ((max_points - (team1_points - team2_points)) / (max_points*2))
            
            odds_team1_win = round((probability_team2_win / (1 - probability_team2_win)) + 1, 1)
            odds_team2_win = round(1 / probability_team2_win, 1)
            odds_draw = round((1 / (probability_draw)), 1)
            
            fixtures_data[match_key]['team1_odds'] = odds_team1_win
            fixtures_data[match_key]['team2_odds'] = odds_team2_win
            fixtures_data[match_key]['draw_odds'] = odds_draw
    return fixtures_data


def get_results(id):
    res = requests.get(f"https://livescore-api.com/api-client/scores/history.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&page=&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    results_data_last_page = res.json()
    last_page = (results_data_last_page['data']['total_pages'])
    res2 = requests.get(f"https://livescore-api.com/api-client/scores/history.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&page=&page={last_page}&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    results_data_last_page = res2.json()
    results = results_data_last_page['data']['match']
    
    results_info = {}

    for index, results, in enumerate(results):
        home_id = results['home_id']
        team1 = results['home_name']
        away_id = results['away_id']
        team2 = results['away_name']
        date = results['date']
        time = results['scheduled']
        outcome = results['outcomes']['full_time']
        match_id = f"{home_id}-{away_id}-{date}"
        results_info[match_id] = {'home_id': home_id, 'team1': team1, 'away_id': away_id, 'team2': team2, 'date': date, 'time': time, 'outcome': outcome}
    return(results_info)

def get_live(id): 
    res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&page=&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    live_data = res.json()
    live_dat = live_data['data']['match']

    live_info = {}

    for index, results, in enumerate(live_dat):
        if results['status'] == 'Finished' or results['time'] == 'FT':
            home_id = results['home_id']
            team1 = results['home_name']
            away_id = results['away_id']
            team2 = results['away_name']
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            date = current_date
            time = results['scheduled']
            outcome = results['outcomes']['full_time']
            match_id = f"{home_id}-{away_id}-{date}"
            live_info[match_id] = {'home_id': home_id, 'team1': team1, 'away_id': away_id, 'team2': team2, 'date': date, 'time': time, 'outcome': outcome}
    return(live_info)
           
if __name__ == "__main__":
    get_live(196)
    