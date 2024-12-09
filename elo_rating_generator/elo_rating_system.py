import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from automation_sql_scripts.reset_elo import reset_elo
from config import DATABASE_URL
from game_elo import fetch_games_in_series, process_game
from series_elo import fetch_all_series, process_series

def generate_elo_rating(conn):
    reset_elo()
    all_series = fetch_all_series(conn)

    for series in all_series:
        series_id, winner, loser, number_of_games, total_score = series      

        winning_team_elo, losing_team_elo = process_series(
            conn,
            series_id=series_id,
            winning_team_id=winner,
            losing_team_id=loser,
            number_of_games=number_of_games,
            total_score=total_score
        )

        games = fetch_games_in_series(conn, series_id)
        for game in games:
            process_game(conn, game, winning_team_elo, losing_team_elo)
    
    print("Elo generated!")


if __name__ == "__main__":
    conn = psycopg2.connect(DATABASE_URL)
    generate_elo_rating(conn)