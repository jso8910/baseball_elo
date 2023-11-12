from scipy.stats import norm

# I did so much work and this is optimal
K_VALUE = 12.6


def apply_elo(winner_elo, loser_elo, weight):
    Qa = pow(10, winner_elo / 400)
    Qb = pow(10, loser_elo / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    winner_new = winner_elo + K_VALUE * (1 - Ea) * weight
    loser_new = loser_elo + K_VALUE * (0 - Eb) * weight
    return winner_new, loser_new


# From downloading player months with PA >= 30 for 2015-2023 and doing a weighted AVERAGE/STDIST on google sheets.
MEAN = 0.3211377343
STD = 0.07252875015


def elo_error(batter_elo, pitcher_elo, actual_woba):
    Qa = pow(10, batter_elo / 400)
    Qb = pow(10, pitcher_elo / 400)
    Ea = Qa / (Qa + Qb)
    # Inverse of the cumulative probability function (so you input a cumulative probability and it returns at what wOBA value that probability is reached)
    xwOBA = norm(MEAN, STD).ppf(Ea)
    return pow(xwOBA - actual_woba, 2)


def predict_matchup_from_elo(batter_elo, pitcher_elo):
    Qa = pow(10, batter_elo / 400)
    Qb = pow(10, pitcher_elo / 400)
    Ea = Qa / (Qa + Qb)
    print(Ea)
    # Inverse of the cumulative probability function (so you input a cumulative probability and it returns at what wOBA value that probability is reached)
    xwOBA = norm(MEAN, STD).ppf(Ea)
    return xwOBA
