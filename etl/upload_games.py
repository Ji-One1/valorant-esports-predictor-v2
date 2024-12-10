import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import psycopg2
from config import DATABASE_URL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def save_data_to_json(data, file_path):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def upload_team_data(team_data):
    return [{"team_id": id, "name": team} for team, id in team_data.items()]


def upload_season_data(jsonFile):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open(jsonFile, encoding='utf-8') as f:
        season_data = json.load(f)
    
    team_data = {}  # To store teams and their UUIDs
    betting_data_to_upload = []
    tournament_data_to_upload = []
    all_series_to_upload = []
    all_games_to_upload = []

    for tournament_data in season_data:
        tournament_name = tournament_data["tournament_name"]
        tournament_id = tournament_data["tournament_id"]
        tournament_data_to_upload.append({'tournament_id': tournament_id, "name": tournament_name})

        series_data = tournament_data["series"]
        for series in series_data:
            if not series: 
                continue
            
            series_id = series["series_id"]
            date = series["date"]
            winner = series["series_winner"]
            loser = series["series_loser"]
        
            if winner not in team_data:
                team_data[winner] = str(uuid.uuid4())
            if loser not in team_data:
                team_data[loser] = str(uuid.uuid4())

            winner_id = team_data[winner]
            loser_id = team_data[loser]

            winner_betting_odds = float(series["betting_odds"])
            loser_betting_odds = find_loser_odds(winner_betting_odds)
            betting_data_to_upload.append({
                "bet_id": str(uuid.uuid4()),
                "series_id": series_id,
                "tournament_id": tournament_id,
                "winner_id": winner_id,
                "loser_id": loser_id,
                "winner_odds": str(winner_betting_odds),
                "loser_odds": str(loser_betting_odds)
            })

            games = series["games"]
            overall_total_rounds = 0
            for game in games:
                game_id = game["game_id"]
                winning_score = int(game["winning_score"])
                losing_score = int(game["losing_score"])
                total_score = winning_score + losing_score
                overall_total_rounds += total_score

                all_games_to_upload.append({
                    'game_id': game_id,
                    "series_id": series_id,
                    'map_name': game["map"],
                    'map_winner': team_data[game["winner"]],
                    'map_loser': team_data[game["loser"]],
                    'winning_score': str(winning_score),
                    'losing_score': str(losing_score),
                    'score': str(total_score)
                })

            all_series_to_upload.append({
                'series_id': series_id,
                'tournament_id': tournament_id,
                'date': date,
                'series_winner': winner_id,
                'series_loser': loser_id,
                'number_of_games': len(games),
                'total_score': str(overall_total_rounds)
            })
            
    save_data_to_json(upload_team_data(team_data), "team_data_2024.json")

    insert_data_into_db(cur, betting_data_to_upload, all_series_to_upload, all_games_to_upload, tournament_data_to_upload, team_data)

    conn.commit()
    cur.close()
    conn.close()


def insert_data_into_db(cur, betting_data, all_series, all_games, tournament_data, team_data):
    for tournament in tournament_data:
        cur.execute("""
            INSERT INTO tournament_data (tournament_id, name)
            VALUES (%s, %s);
        """, (tournament['tournament_id'], tournament['name']))

    for team in upload_team_data(team_data):
        cur.execute("""
            INSERT INTO team_data (team_id, name)
            VALUES (%s, %s);
        """, (team['team_id'], team['name']))

    for series in all_series:
        cur.execute("""
            INSERT INTO series (series_id, tournament_id, date, series_winner, series_loser, number_of_games, total_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (series['series_id'], series['tournament_id'], series['date'], series['series_winner'], series['series_loser'], series['number_of_games'], series['total_score']))

    for game in all_games:
        cur.execute("""
            INSERT INTO games (game_id, series_id, map_name, map_winner, map_loser, winning_score, losing_score, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (game['game_id'], game['series_id'], game['map_name'], game['map_winner'], game['map_loser'], game['winning_score'], game['losing_score'], game['score']))

    for bet in betting_data:
        cur.execute("""
            INSERT INTO betting_data (bet_id, series_id, tournament_id, winner_id, loser_id, winner_odds, loser_odds)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (bet["bet_id"], bet['series_id'], bet['tournament_id'], bet['winner_id'], bet['loser_id'], bet['winner_odds'], bet['loser_odds']))


def find_loser_odds(winner_betting_odds):
    bookmaker_margin = 0.07
    winning_team_implied_odds = winner_betting_odds
    losing_team_implied_odds = 1 / ((1 + bookmaker_margin) - (1 / winning_team_implied_odds))
    
    return losing_team_implied_odds


if __name__ == "__main__":
    upload_season_data("season_data_vct-2024.json")
    print("Data Uploaded Successfully!")
