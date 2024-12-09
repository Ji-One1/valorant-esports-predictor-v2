def calculate_expected_score(R_A, R_B):
    return 1 / (1 + 10 ** ((R_B - R_A) / 400))

def calculate_mov_multiple(total_score, number_of_games):
    return  (24) /( total_score / number_of_games )

def update_elo_rating(rating_a, rating_b, actual_score_a, actual_score_b, number_of_games, total_score):
    
    K = 40 #Base adjustment factor
    expected_a = calculate_expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a
    
    elo_adjustment_a = K * (actual_score_a - expected_a)
    elo_adjustment_b = K * (actual_score_b - expected_b)
    
    mov_multiplier = calculate_mov_multiple(total_score, number_of_games)
    
    new_rating_a = rating_a + elo_adjustment_a * mov_multiplier
    new_rating_b = rating_b + elo_adjustment_b * mov_multiplier
    
    return new_rating_a, new_rating_b