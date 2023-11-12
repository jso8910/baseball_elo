"""
Redefine the weights around an out having a value of 0.5, and a strikeout having a value of 1.
"""

import csv

with open("weights_averages/woba_weights.csv", "r") as f:
    reader = list(csv.DictReader(f))

for key, val in reader[0].items():
    reader[0][key] = float(reader[0][key]) + 0.5

# A strikeout is a bonus for a pitcher
reader[0]["K"] += 0.3
reader[0]["Out"] += 0.2

# Slight bonus for an IBB
reader[0]["IBB"] = reader[0]["UBB"] / 3

with open("weights_averages/elo_weights.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=reader[0].keys())
    writer.writeheader()
    writer.writerows(reader)
