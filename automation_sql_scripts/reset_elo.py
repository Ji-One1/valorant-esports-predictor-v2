import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

def reset_elo():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        all_maps = ['lotus', 'abyss', 'haven', 'sunset', 'split', 'icebox', 'breeze', 'bind', 'ascent', 'fracture', 'pearl']

        with conn.cursor() as cursor:
            for map in all_maps:
                cursor.execute(f"UPDATE team_data SET {map}_elo = %s", (1500,))
            cursor.execute(f"UPDATE team_data SET current_elo = %s", (1500,))
            conn.commit()
            
        print("Reset Done!")

    except Exception as error:
        print(f"Error creating schema: {error}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reset_elo()