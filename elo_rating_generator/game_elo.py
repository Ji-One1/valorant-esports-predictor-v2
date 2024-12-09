from elo_helper_functions import calculate_expected_score, update_elo_rating


def get_current_team_elo_based_on_map(conn, team_id, map):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT {map}_elo FROM team_data WHERE team_id = %s", (team_id,))
        result = cursor.fetchone()
        return result[0] if result else 1500
    
def update_game_elo(conn, game_id, winning_team_elo, losing_team_elo, winning_team_odds):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE games
            SET winner_elo_before = %s, loser_elo_before = %s,
                winning_team_odds = %s
            WHERE game_id = %s
        """, (winning_team_elo, losing_team_elo, winning_team_odds , game_id))
        conn.commit()

def update_current_team_elo_map(conn, team_id, new_rating, map):
    with conn.cursor() as cursor:
        cursor.execute(f"UPDATE team_data SET {map}_elo = %s WHERE team_id = %s", (new_rating, team_id))
        conn.commit()

def combined_elo(team_elo, map_elo, map_elo_worth):
    print(team_elo, map_elo, map_elo_worth)
    return (1 - map_elo_worth) * team_elo + (map_elo_worth) * map_elo


def fetch_games_in_series(conn, series_id):
        with conn.cursor() as cursor: 
            cursor.execute(f"SELECT game_id, map_name, map_winner, map_loser, score FROM games WHERE series_id = %s", (series_id,))
            return cursor.fetchall()
        
def process_game(conn, game, winning_team_overall_elo_before, losing_team_overall_elo_before):
    game_id, map_name, winning_team_id, losing_team_id, score  = game

    winning_team_map_elo_before = get_current_team_elo_based_on_map(conn, winning_team_id, map_name)
    losing_team_map_elo_before = get_current_team_elo_based_on_map(conn, losing_team_id, map_name)
    
    winning_team_combined_elo_before = combined_elo(winning_team_overall_elo_before, winning_team_map_elo_before, 0.3) 
    losing_team_combined_elo_before = combined_elo(losing_team_overall_elo_before, losing_team_map_elo_before, 0.3)


    if winning_team_combined_elo_before is None or losing_team_combined_elo_before is None:
        print(f"Rating for {winning_team_id} or {losing_team_id} not found.")
        return

    S_A = 1 
    S_B = 0 
   
    winning_team_odds = calculate_expected_score(winning_team_combined_elo_before, losing_team_combined_elo_before)
    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_combined_elo_before, losing_team_combined_elo_before, S_A, S_B, 1, score)

    update_game_elo(conn, game_id, winning_team_combined_elo_before, losing_team_combined_elo_before, winning_team_odds)
    update_current_team_elo_map(conn, winning_team_id, new_winner_elo, map_name)
    update_current_team_elo_map(conn, losing_team_id, new_loser_elo, map_name)