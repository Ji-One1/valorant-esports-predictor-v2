import psycopg2

def fetch_all_series(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT winning_team_odds, tournament_id FROM series ORDER BY date ASC")
        return cursor.fetchall()

def evaluate_elo_accuracy(all_series, tournament):
    win_count = 0
    total_count = 0
    brier_score = 0.0

    for series in all_series:
        tournament_id = series[1]

        if  tournament_id != tournament:
            continue
        winner_odds = series[0]
        

        if winner_odds == 0.5:
            continue

        loser_odds = 1 - winner_odds  
        if winner_odds > loser_odds:
            win_count += 1

        total_count += 1
        brier_score += (winner_odds - 1) ** 2

    accuracy = win_count / total_count if total_count > 0 else 0
    avg_brier_score = brier_score / total_count if total_count > 0 else 0
    return accuracy, avg_brier_score

def main():
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DATABASE_URL
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        all_series = fetch_all_series(conn)

    finally:
        if conn:
            conn.close()
    accuracy, avg_brier_score = evaluate_elo_accuracy(all_series, "339d9964-0bac-42b4-a88a-e75ba4e4735f")

    print(f'SERIES: Accuracy of Elo predictions: {accuracy:.2%}')
    print(f'SERIES: Average Brier Score: {avg_brier_score:.4f}')

if __name__ == "__main__":
    main()

    