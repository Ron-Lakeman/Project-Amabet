import requests
import json

def main():
    # res1 = requests.get("https://livescore-api.com/api-client/fixtures/matches.json?competition_id=196&key=GNbdgm8Y4WMM0rXE&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")

    # fixtures_data = res1.json()
    # fixtures = fixtures_data['data']['fixtures']

    # for fixture in fixtures:
    #     home_team = fixture['home_name']
    #     away_team = fixture['away_name']
    #     print(f"Home Team: {home_team}, Away Team: {away_team}")

    res2 = requests.get("https://livescore-api.com/api-client/leagues/table.json?competition_id=196&key=GNbdgm8Y4WMM0rXE&secret=EmyxlamXomfGzDhfrstIPCGUysGzUDdy")
    standings_data = res2.json()
    
    standings = standings_data['data']['table']

    for team in standings:
        rank = team['rank']
        matches = team['matches']
        team_name = team['name']
        points = team['points']
        won = team['won']
        lost = team['lost']
        draw = team['drawn']
        print(f"{rank:2}: {team_name:20}  {matches:2}, W{won:<2}, D{draw:<2}, L{lost:<2}: P{points:2}")



if __name__ == "__main__":
    main()