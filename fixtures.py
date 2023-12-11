import requests
import json
import math

def get_ranking(id):
    res = requests.get(f" https://livescore-api.com/api-client/leagues/table.json?competition_id={id}&key=GNbdgm8Y4WMM0rXE&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    ranking_data = res.json()
    ranking = ranking_data['data']['table']
    # print(ranking)
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
    print(fixtures)

    for index, match in enumerate(fixtures):
        home_id = match['home_id']
        team1 = match['home_name']
        away_id = match['away_id']
        team2 = match['away_name']
        date = match['date']
        location = match['location']
        time = match['time']
        match_info[index] = {'home_id': home_id, 'team1': team1, 'away_id': away_id, 'team2': team2, 'date': date, 'location': location, 'time': time}
    
    return(match_info)
        

def get_fixtures_and_rank(id):
    ranking_data = get_ranking(id)
    fixtures_data = get_fixtures(id)
    
    for rank_key, x in ranking_data.items():
        for match_key, y in fixtures_data.items():
            # print(f"ranking: {ranking_data[rank_key]['team']} - {ranking_data[rank_key]['team_id']}")
            # print(f"home: {fixtures_data[match_key]['team1']} - {fixtures_data[match_key]['home_id']}")
            # print(f"away: {fixtures_data[match_key]['team2']} - {fixtures_data[match_key]['away_id']}")

            # print(f"ranking_id: ({ranking_data[rank_key]['team_id']}) - fixture_id: ({fixtures_data[match_key]['home_id']})")
            if str(fixtures_data[match_key]['home_id']) == str(ranking_data[rank_key]['team_id']):

                fixtures_data[match_key]['team1_ranking'] = ranking_data[rank_key]['rank']
                fixtures_data[match_key]['team1_points'] = ranking_data[rank_key]['points']
                fixtures_data[match_key]['team1_matches'] = ranking_data[rank_key]['matches']

            elif str(ranking_data[rank_key]['team_id']) == str(fixtures_data[match_key]['away_id']):
                fixtures_data[match_key]['team2_ranking'] = ranking_data[rank_key]['rank']
                fixtures_data[match_key]['team2_points'] = ranking_data[rank_key]['points']
                fixtures_data[match_key]['team2_matches'] = ranking_data[rank_key]['matches']

    # print(fixtures_data)
    return fixtures_data
            
def calculate_odds(id):
    fixtures_data = get_fixtures_and_rank(id)
    print(fixtures_data)


    for rank_key, x in fixtures_data.items():
        for match_key, y in fixtures_data.items():
            team1_points = int(fixtures_data[match_key]['team1_points'])
            team2_points = int(fixtures_data[match_key]['team2_points'])
            # points_difference = int(team1_points) - int(team2_points)
            # print(points_difference)
            # exponent = -(beta_0 + beta_1 * points_difference)
            # probability_team1_win = 1 / (1 + math.exp(exponent))
            # probability_team2_win = 1 - probability_team1_win
            # probability_draw = 1 - probability_team1_win

            probability_team1_win = team1_points / (team1_points + team2_points)
            probability_team2_win = team2_points / (team1_points + team2_points)
            max_points = int(fixtures_data[rank_key]['team1_matches']) * 3
            # print(max_points)
            probability_draw = ((max_points - (team1_points - team2_points)) / (max_points*2))

            # print(probability_draw)

            # print(f"The prob of team2 winning are: {probability_team1_win:.2f}")
            # print(f"The prob of team2 winning are: {probability_team2_win:.2f}")
            
            odds_team1_win = round((probability_team2_win / (1 - probability_team2_win)) + 1, 1)
            odds_team2_win = round(1 / probability_team2_win, 1)
            odds_draw = round((1 / (probability_draw)), 1)
            # print(odds_draw)

            fixtures_data[match_key]['team1_odds'] = odds_team1_win
            fixtures_data[match_key]['team2_odds'] = odds_team2_win
            fixtures_data[match_key]['draw_odds'] = odds_draw
    
    print(fixtures_data)
    return fixtures_data


if __name__ == "__main__":
    id = 196
    # get_fixtures_and_rank(id)
    calculate_odds(id)






  


