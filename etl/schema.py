import psycopg2
from psycopg2 import sql
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

# Function to create the tables
def create_schema():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        create_team_data_table = """
        CREATE TABLE IF NOT EXISTS team_data (
            team_id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            current_elo INT DEFAULT 1500,
            fracture_elo INT DEFAULT 1500,
            pearl_elo INT DEFAULT 1500,
            lotus_elo INT DEFAULT 1500,
            abyss_elo INT DEFAULT 1500,
            haven_elo INT DEFAULT 1500,
            sunset_elo INT DEFAULT 1500,
            split_elo INT DEFAULT 1500,
            icebox_elo INT DEFAULT 1500,
            breeze_elo INT DEFAULT 1500,
            bind_elo INT DEFAULT 1500,
            ascent_elo INT DEFAULT 1500
        );
        """
        
        create_tournament_data_table = """
        CREATE TABLE IF NOT EXISTS tournament_data (
            tournament_id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        
        create_series_table = """
        CREATE TABLE IF NOT EXISTS series (
            series_id UUID PRIMARY KEY,
            tournament_id UUID REFERENCES tournament_data(tournament_id) ON DELETE CASCADE,
            date DATE NOT NULL,
            series_winner UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            series_loser UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            number_of_games INT NOT NULL,
            total_score INT NOT NULL,
            winner_elo_before INT,
            loser_elo_before INT,
            winning_team_odds FLOAT
        );
        """
        
        create_games_table = """
        CREATE TABLE IF NOT EXISTS games (
            game_id UUID PRIMARY KEY,
            series_id UUID REFERENCES series(series_id) ON DELETE CASCADE,
            map_name VARCHAR(255) NOT NULL,
            map_winner UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            map_loser UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            winning_score INT NOT NULL,
            losing_score INT NOT NULL,
            score INT NOT NULL,
            winner_elo_before INT,
            loser_elo_before INT,
            winning_team_odds FLOAT
        );
        """
        
        create_betting_data_table = """
        CREATE TABLE IF NOT EXISTS betting_data (
            bet_id UUID PRIMARY KEY,
            series_id UUID REFERENCES series(series_id) ON DELETE CASCADE,
            tournament_id UUID REFERENCES tournament_data(tournament_id) ON DELETE CASCADE,
            winner_id UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            loser_id UUID REFERENCES team_data(team_id) ON DELETE CASCADE,
            winner_odds DECIMAL(10, 2) NOT NULL,
            loser_odds DECIMAL(10, 2) NOT NULL
        );
        """
        
        # Execute the SQL commands to create tables
        cursor.execute(create_team_data_table)
        cursor.execute(create_tournament_data_table)
        cursor.execute(create_series_table)
        cursor.execute(create_games_table)
        cursor.execute(create_betting_data_table)

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        print("Schema created successfully!")

    except Exception as error:
        print(f"Error creating schema: {error}")
    finally:
        if connection:
            connection.close()

# Call the function to create the schema
if __name__ == "__main__":
    create_schema()
