from elo_helper_functions import calculate_expected_score, update_elo_rating

def get_current_team_elo(conn, team_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT current_elo FROM team_data WHERE team_id = %s", (team_id,))
        result = cursor.fetchone()
        return result[0] if result else 1500
    
    
def update_series_elo(conn, series_id, winning_team_elo, losing_team_elo, winning_team_odds):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE series
            SET winner_elo_before = %s, loser_elo_before = %s,
                winning_team_odds = %s
            WHERE series_id = %s
        """, (winning_team_elo, losing_team_elo, winning_team_odds , series_id))
        conn.commit()

def update_current_team_elo(conn, team_id, new_rating):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE team_data SET current_elo = %s WHERE team_id = %s", (new_rating, team_id))
        conn.commit()

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT series_id, series_winner, series_loser, number_of_games, total_score FROM series ORDER BY date ASC") 
        return cursor.fetchall()
    
def process_series(conn, series_id, winning_team_id, losing_team_id, number_of_games, total_score):
    
    winning_team_elo_before = get_current_team_elo(conn, winning_team_id)
    losing_team_elo_before = get_current_team_elo(conn, losing_team_id)

    if winning_team_elo_before is None or losing_team_elo_before is None:
        print(f"Rating for {winning_team_id} or {losing_team_id} not found.")
        return
    
    winning_team_odds = calculate_expected_score(winning_team_elo_before, losing_team_elo_before)

    S_A = 1 
    S_B = 0 

    new_winner_elo, new_loser_elo = update_elo_rating(winning_team_elo_before, losing_team_elo_before, S_A, S_B, number_of_games, total_score)

    update_series_elo(conn, series_id, winning_team_elo_before, losing_team_elo_before, winning_team_odds)

    update_current_team_elo(conn, winning_team_id, new_winner_elo)
    update_current_team_elo(conn, losing_team_id, new_loser_elo)

    return winning_team_elo_before, losing_team_elo_before