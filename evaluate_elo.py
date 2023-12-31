import argparse
import csv
import datetime
import os
import sys
from copy import deepcopy

import pandas as pd
import tqdm

from apply_elo import apply_elo
from config import end_data_year, start_data_year


# IBBs are included but they're worth 1/3 of a UBB
def evaluate_elo(plays):
    event_code_to_event = {
        2: "Out",
        3: "K",
        14: "UBB",
        15: "IBB",
        16: "HBP",
        20: "1B",
        21: "2B",
        22: "3B",
        23: "HR",
    }
    batter_win_events = ["UBB", "HBP", "1B", "2B", "3B", "HR", "IBB"]
    pitcher_win_events = ["Out", "K"]
    with open("weights_averages/elo_weights.csv", "r") as f:
        reader = list(csv.DictReader(f))
    elo_weights = {key: float(val) for key, val in reader[0].items()}
    batter_elos = [
        [
            "batter",
            "end of period elo",
            "peak elo",
            "peak elo gameid",
            "lowest elo",
            "lowest elo gameid",
            "pa",
        ]
    ]
    pitcher_elos = [
        [
            "pitcher",
            "end of period elo",
            "peak elo",
            "peak elo gameid",
            "lowest elo",
            "lowest elo gameid",
            "pa",
        ]
    ]
    batters = ["header NOT FOR USE"]
    pitchers = ["header nOT FOR USE"]

    month_batter_elos = {}
    month_pitcher_elos = {}
    start_of_year_batter_elos = {}
    start_of_year_pitcher_elos = {}

    for _, play in tqdm.tqdm(plays.iterrows(), total=plays.shape[0]):
        if int(play["EVENT_CD"]) not in event_code_to_event:
            continue
        event = int(play["EVENT_CD"])
        batter = play["BAT_ID"]
        pitcher = play["PIT_ID"]

        # Save things as they were as of that month
        if (
            play["date"].day == 1
            and play["date"].strftime("%Y%m%d") not in month_batter_elos
        ):
            month_batter_elos[play["date"].strftime("%Y%m%d")] = deepcopy(batter_elos)
            month_pitcher_elos[play["date"].strftime("%Y%m%d")] = deepcopy(pitcher_elos)

        # Save things as they were at the start of the year
        if play["date"].year not in start_of_year_batter_elos:
            start_of_year_batter_elos[play["date"].year] = deepcopy(batter_elos)
            start_of_year_pitcher_elos[play["date"].year] = deepcopy(pitcher_elos)

        # Define the default (and thus average) ELO to be 1000
        if not batter in batters:
            batter_elos.append(
                [batter, 1000.0, 1000.0, play["GAME_ID"], 1000.0, play["GAME_ID"], 0]
            )
            batters.append(batter)
        if not pitcher in pitchers:
            pitcher_elos.append(
                [pitcher, 1000.0, 1000.0, play["GAME_ID"], 1000.0, play["GAME_ID"], 0]
            )
            pitchers.append(pitcher)

        batter_index = batters.index(batter)
        pitcher_index = pitchers.index(pitcher)
        batter_elo = batter_elos[batter_index][1]
        pitcher_elo = pitcher_elos[pitcher_index][1]

        event_str = event_code_to_event[event]
        if event_str in batter_win_events:
            batter_elo, pitcher_elo = apply_elo(
                batter_elo, pitcher_elo, elo_weights[event_str]
            )
        elif event_str in pitcher_win_events:
            pitcher_elo, batter_elo = apply_elo(
                pitcher_elo, batter_elo, elo_weights[event_str]
            )
        else:
            raise ValueError(
                f"Event {event_str} not in batter_win_events or pitcher_win_events"
            )
        batter_elos[batter_index][1] = batter_elo
        pitcher_elos[pitcher_index][1] = pitcher_elo
        if batter_elo > batter_elos[batter_index][2]:
            batter_elos[batter_index][2] = batter_elo
            batter_elos[batter_index][3] = play["GAME_ID"]
        if pitcher_elo > pitcher_elos[pitcher_index][2]:
            pitcher_elos[pitcher_index][2] = pitcher_elo
            pitcher_elos[pitcher_index][3] = play["GAME_ID"]

        if batter_elo < batter_elos[batter_index][4]:
            batter_elos[batter_index][4] = batter_elo
            batter_elos[batter_index][5] = play["GAME_ID"]
        if pitcher_elo < pitcher_elos[pitcher_index][4]:
            pitcher_elos[pitcher_index][4] = pitcher_elo
            pitcher_elos[pitcher_index][5] = play["GAME_ID"]

        batter_elos[batter_index][6] += 1
        pitcher_elos[pitcher_index][6] += 1
    return (
        batter_elos,
        pitcher_elos,
        month_batter_elos,
        month_pitcher_elos,
        start_of_year_batter_elos,
        start_of_year_pitcher_elos,
    )


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
    plays["date"] = plays["GAME_ID"].apply(
        lambda x: datetime.datetime.fromisoformat(x[3:-1])
    )
    plays.sort_values("date", ascending=True, inplace=True)
    (
        batter_elos,
        pitcher_elos,
        month_batter_elos,
        month_pitcher_elos,
        start_of_year_batter_elos,
        start_of_year_pitcher_elos,
    ) = evaluate_elo(plays)
    with open("pitcher_elo.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(pitcher_elos)
    with open("hitter_elo.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(batter_elos)

    for directory in [
        "monthly_elo_data/hitter/",
        "monthly_elo_data/pitcher/",
        "yearly_elo_data/hitter/",
        "yearly_elo_data/pitcher/",
    ]:
        if not os.path.isdir(directory):
            os.mkdir(directory)
        for filename in os.listdir(directory):
            os.remove(directory + filename)

    for key, val in month_batter_elos.items():
        with open(f"monthly_elo_data/hitter/{key}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(val)

    for key, val in month_pitcher_elos.items():
        with open(f"monthly_elo_data/pitcher/{key}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(val)

    for key, val in start_of_year_batter_elos.items():
        with open(f"yearly_elo_data/hitter/{key}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(val)

    for key, val in start_of_year_pitcher_elos.items():
        with open(f"yearly_elo_data/pitcher/{key}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(val)


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
