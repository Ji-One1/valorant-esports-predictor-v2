import psycopg2

def get_model_odds(conn, series_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            winning_team_odds  
        FROM 
            series  
        WHERE 
            series_id = %s

    """, (str(series_id),))
    winner_odds = cur.fetchone()
    loser_odds = 1 - winner_odds[0]
    return (winner_odds[0], loser_odds)

def calculate_ev(probability, odds):
    return (probability * odds) - 1

def ev_predictor(model_odds, betting_odds):
    ev_winning_team = calculate_ev(model_odds[0], betting_odds["winner_odds"])
    ev_losing_team = calculate_ev(model_odds[1], betting_odds["loser_odds"])
    return ev_winning_team, ev_losing_team

def fetch_betting_data_by_tournament(conn, tournament_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            series_id, 
            tournament_id, 
            winner_odds, 
            loser_odds, 
            winner_id, 
            loser_id
        FROM betting_data
        WHERE tournament_id = %s
    """, (tournament_id,))
    
    rows = cur.fetchall()
    
    betting_data = []
    for row in rows:
        betting_data.append({
            "series_id": row[0],
            "winner_odds": row[2],
            "loser_odds": row[3],
            "winner_id": row[4],
            "loser_id": row[5],
        })
    return betting_data


def find_betworthy_games(conn, tournament_ids):
    tournament_to_check = []
    for tournament_id in tournament_ids:
        series_to_check = []
        betting_data = fetch_betting_data_by_tournament(conn, tournament_id)
        for series in betting_data:
            current_series = {"series_id": series["series_id"], "betting_team" : False, "ev": None}
            model_odds = get_model_odds(conn, series["series_id"])
            ev_winning_team, ev_losing_team = ev_predictor(model_odds, series)
            if ev_winning_team > 0.05 and ev_winning_team < 1.4:
                current_series["betting_team"] = series["winner_id"] 
                current_series["ev"] = ev_winning_team
                current_series["outcome"] = "win"
                current_series["betting_odds"] = series["winner_odds"]
            elif ev_losing_team > 0.05 and ev_losing_team < 1.4:
                current_series["betting_team"] = series["loser_id"] 
                current_series["ev"] = ev_losing_team
                current_series["outcome"] = "lose"
                current_series["betting_odds"] = series["loser_odds"]
            
            if current_series["betting_team"]:
                series_to_check.append(current_series)
        tournament_to_check.append(series_to_check)
    return tournament_to_check


def games_chosen_by_public_favoured(conn, tournament_ids):
    tournament_to_check = []
    for tournament_id in tournament_ids:
        series_to_check = []
        betting_data = fetch_betting_data_by_tournament(conn, tournament_id)
        for series in betting_data:
            current_series = {"series_id": series["series_id"], "betting_team" : False, "ev": None}
            model_odds = get_model_odds(conn, series["series_id"])
            ev_winning_team, ev_losing_team = ev_predictor(model_odds, series)

            if series["winner_odds"] < series["loser_odds"]:
                current_series["betting_team"] = series["winner_id"] 
                current_series["ev"] = ev_winning_team
                current_series["outcome"] = "win"
                current_series["betting_odds"] = series["winner_odds"]
            else:
                current_series["betting_team"] = series["loser_id"] 
                current_series["ev"] = ev_losing_team
                current_series["outcome"] = "lose"
                current_series["betting_odds"] = series["loser_odds"]
            
            if current_series["betting_team"]:
                series_to_check.append(current_series)
        tournament_to_check.append(series_to_check)
    return tournament_to_check

def games_chosen_by_public_unfavoured(conn, tournament_ids):
    tournament_to_check = []
    for tournament_id in tournament_ids:
        series_to_check = []
        betting_data = fetch_betting_data_by_tournament(conn, tournament_id)
        for series in betting_data:
            current_series = {"series_id": series["series_id"], "betting_team" : False, "ev": None}
            model_odds = get_model_odds(conn, series["series_id"])
            ev_winning_team, ev_losing_team = ev_predictor(model_odds, series)

            if series["winner_odds"] > series["loser_odds"]:
                current_series["betting_team"] = series["winner_id"] 
                current_series["ev"] = ev_winning_team
                current_series["outcome"] = "win"
                current_series["betting_odds"] = series["winner_odds"]
            else:
                current_series["betting_team"] = series["loser_id"] 
                current_series["ev"] = ev_losing_team
                current_series["outcome"] = "lose"
                current_series["betting_odds"] = series["loser_odds"]
            
            if current_series["betting_team"]:
                series_to_check.append(current_series)
        tournament_to_check.append(series_to_check)
    return tournament_to_check

def games_chosen_randomly(conn, tournament_ids):
    import random
    tournament_to_check = []
    for tournament_id in tournament_ids:
        series_to_check = []
        betting_data = fetch_betting_data_by_tournament(conn, tournament_id)
        for series in betting_data:
            current_series = {"series_id": series["series_id"], "betting_team" : False, "ev": None}
            model_odds = get_model_odds(conn, series["series_id"])
            ev_winning_team, ev_losing_team = ev_predictor(model_odds, series)
            random_choice = random.choices(
                    [True, False],
                    weights=[1/series["winner_odds"], 1/series["loser_odds"]],
                    k=1
                )[0]
            if not random_choice:
                current_series["betting_team"] = series["winner_id"] 
                current_series["ev"] = ev_winning_team
                current_series["outcome"] = "win"
                current_series["betting_odds"] = series["winner_odds"]
            else:
                current_series["betting_team"] = series["loser_id"] 
                current_series["ev"] = ev_losing_team
                current_series["outcome"] = "lose"
                current_series["betting_odds"] = series["loser_odds"]
            
            if current_series["betting_team"]:
                series_to_check.append(current_series)

        tournament_to_check.append(series_to_check)
    return tournament_to_check



if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DATABASE_URL

    try:
        conn = psycopg2.connect(DATABASE_URL)
        games_chosen_randomly(conn, ["339d9964-0bac-42b4-a88a-e75ba4e4735f"])
    finally:
        if conn:
            conn.close()
   
   