import argparse
import csv
import os
import sys

import pandas as pd
import tqdm

from apply_elo import K_VALUE, elo_error

start_data_year = 1913
end_data_year = 2022


def test_elo(plays):
    with open("hitter_elo.csv", "r") as f:
        reader = list(csv.DictReader(f))
    hitter_elos = {}
    for row in reader:
        hitter_elos[row["batter"]] = float(row["end of career elo"])
    with open("pitcher_elo.csv", "r") as f:
        reader = list(csv.DictReader(f))
    pitcher_elos = {}
    for row in reader:
        pitcher_elos[row["pitcher"]] = float(row["end of career elo"])

    event_code_to_event = {
        2: "Out",
        3: "K",
        14: "UBB",
        16: "HBP",
        20: "1B",
        21: "2B",
        22: "3B",
        23: "HR",
    }
    with open("weights_averages/woba_weights.csv", "r") as f:
        reader = list(csv.DictReader(f))
    woba_weights = {key: float(val) for key, val in reader[0].items()}
    woba_max = max(woba_weights.values())
    error = 0
    num_plays = 0
    for _, play in tqdm.tqdm(plays.iterrows(), total=plays.shape[0]):
        event = int(play["EVENT_CD"])
        batter = play["BAT_ID"]
        pitcher = play["PIT_ID"]
        if int(play["EVENT_CD"]) not in event_code_to_event:
            continue
        if batter not in hitter_elos:
            continue
        if pitcher not in pitcher_elos:
            continue
        batter_elo = hitter_elos[batter]
        pitcher_elo = pitcher_elos[pitcher]
        weight = woba_weights[event_code_to_event[event]]
        error += elo_error(batter_elo, pitcher_elo, weight)
        num_plays += 1
    return error / num_plays


def main(start_year: int, end_year: int):
    if start_year > end_year:
        print("START_YEAR must be less than END_YEAR", file=sys.stderr)
        sys.exit(1)
    elif start_year < start_data_year or end_year > end_data_year:
        print(
            f"START_YEAR and END_YEAR must be between {start_data_year} and {end_data_year}. If {end_data_year + 1} or a future year has been added to retrosheet, feel free to edit this file.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isdir("data"):
        print(
            "The folder data doesn't exist. Have you run retrosheet_to_csv.sh?",
            file=sys.stderr,
        )
        sys.exit(1)
    files = sorted(os.listdir("data"))
    if not len(files):
        print(
            "The folder data doesn't have any files. Have you run retrosheet_to_csv.sh?",
            file=sys.stderr,
        )
        sys.exit(1)

    files_filtered = []
    for file in files:
        if int(file[0:4]) < start_year or int(file[0:4]) > end_year:  # type: ignore
            continue
        else:
            files_filtered.append(file)  # type: ignore
    years = []

    for _, file in enumerate(tqdm.tqdm(files_filtered)):  # type: ignore
        if int(file[0:4]) < start_year or int(file[0:4]) > end_year:  # type: ignore
            continue
        file = "data/" + file  # type: ignore
        reader = pd.read_csv(  # type: ignore
            file,  # type: ignore
        )
        years.append(reader)  # type: ignore
        del reader
    plays = pd.concat(years)  # type: ignore
    del years
    error = test_elo(plays)
    print(K_VALUE, error)
    # with open("pitcher_elo.csv", "w") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(pitcher_elo)
    # with open("hitter_elo.csv", "w") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(hitter_elo)
    # pitcher_elo.to_csv("pitcher_elo.csv", index=False)
    # hitter_elo.to_csv("hitter_elo.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start-year",
        "-s",
        help=f"Start year of data gathering (defaults to {start_data_year} for the first year of statcast data)",
        type=int,
        default=start_data_year,
    )
    parser.add_argument(
        "--end-year",
        "-e",
        help=f"End year of data gathering (defaults to {end_data_year}, current retrosheet year as of coding)",
        type=int,
        default=end_data_year,
    )

    args = parser.parse_args(sys.argv[1:])
    main(args.start_year, args.end_year)
