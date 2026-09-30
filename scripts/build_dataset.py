"""Build the F1 datasets from FastF1: the notebook 01 pipeline as a script.

Writes two parquet files to data/:
  - laps_clean.parquet   one clean lap per row (lap-time regression)
  - driver_race.parquet  one driver per race (podium classification)

    python scripts/build_dataset.py              # 2023-2024 -> laps_clean, driver_race
    python scripts/build_dataset.py --all        # 2018-2024 -> laps_all, driver_race_all
    python scripts/build_dataset.py 2022 2023    # chosen seasons -> laps_clean, driver_race

The first run downloads every session into cache/ and takes some time;
later runs read the cache.

The first two commands reproduce the committed files in data/. The third overwrites
laps_clean and driver_race, which notebooks 02-05 read.
"""

import os
import sys
import warnings

import fastf1
import numpy as np
import pandas as pd

if {"-h", "--help"} & set(sys.argv[1:]):
    print(__doc__)
    sys.exit()

warnings.simplefilter("ignore")
fastf1.set_log_level("ERROR")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")
DATA = os.path.join(ROOT, "data")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(DATA, exist_ok=True)
fastf1.Cache.enable_cache(CACHE)

ALL = "--all" in sys.argv[1:]
SEASONS = [int(s) for s in sys.argv[1:] if s != "--all"] or (
    list(range(2018, 2025)) if ALL else [2023, 2024]
)
LAPS_OUT, DR_OUT = (
    ("laps_all", "driver_race_all") if ALL else ("laps_clean", "driver_race")
)

KEEP_LAPS = [
    "Season",
    "Round",
    "EventName",
    "race_id",
    "Driver",
    "Team",
    "LapNumber",
    "Stint",
    "Compound",
    "TyreLife",
    "FreshTyre",
    "AirTemp",
    "TrackTemp",
    "Humidity",
    "Pressure",
    "WindSpeed",
    "Rainfall",
    "LapTime_s",
]


def quali_gap(season, rnd):
    """Gap to pole in seconds per driver, from the qualifying session ('Q', not 'R')."""
    try:
        q = fastf1.get_session(season, rnd, "Q")
        q.load(telemetry=False, weather=False, messages=False)
    except Exception as e:
        print(f"    [quali skip] {season} R{rnd}: {e}")
        return None
    r = q.results.copy()
    for c in ["Q1", "Q2", "Q3"]:
        r[c + "_s"] = pd.to_timedelta(r[c]).dt.total_seconds()
    r["quali_best_s"] = r[["Q1_s", "Q2_s", "Q3_s"]].min(axis=1)
    pole = r["quali_best_s"].min()
    r["quali_gap_s"] = r["quali_best_s"] - pole
    return r[["Abbreviation", "quali_gap_s"]]


def main():
    all_laps, all_dr = [], []
    for season in SEASONS:
        sched = fastf1.get_event_schedule(season, include_testing=False)
        rounds = sched[sched["RoundNumber"] > 0][["RoundNumber", "EventName"]]
        print(f"== season {season}: {len(rounds)} rounds ==")
        for _, row in rounds.iterrows():
            rnd, name = int(row["RoundNumber"]), row["EventName"]
            race_id = f"{season}_{rnd:02d}"
            try:
                s = fastf1.get_session(season, rnd, "R")
                s.load()

                laps = s.laps
                if laps is None or len(laps) == 0:
                    print(f"  [skip] {race_id} {name}: no laps")
                    continue

                # weather at the time of each lap
                w = laps.get_weather_data().reset_index(drop=True)
                laps = laps.reset_index(drop=True)
                laps = pd.concat([laps, w.drop(columns=["Time"])], axis=1)
                laps["Season"], laps["Round"] = season, rnd
                laps["EventName"], laps["race_id"] = name, race_id

                res = s.results.copy()
                res["Season"], res["Round"] = season, rnd
                res["EventName"], res["race_id"] = name, race_id
                gap = quali_gap(season, rnd)
                if gap is not None:
                    res = res.merge(gap, on="Abbreviation", how="left")
                else:
                    res["quali_gap_s"] = np.nan
            except Exception as e:
                print(f"  [skip] {race_id} {name}: {type(e).__name__}: {e}")
                continue

            # keep a round only when all of it loaded, so laps and results stay consistent
            all_laps.append(laps)
            all_dr.append(res)
            ngap = res["quali_gap_s"].notna().sum()
            print(
                f"  [ok] {race_id} {name:<28} laps={len(laps):>4} quali_gap={ngap:>2}/{len(res)}"
            )

    laps_raw = pd.concat(all_laps, ignore_index=True)
    res_raw = pd.concat(all_dr, ignore_index=True)

    # laps: timed, no pit in/out laps, green flag, accurate timing, within 107% of the race's fastest
    c = laps_raw.copy()
    c = c[c["LapTime"].notna()]
    c = c[c["PitInTime"].isna() & c["PitOutTime"].isna()]
    c = c[c["TrackStatus"].astype(str) == "1"]
    c = c[c["IsAccurate"] == True]  # noqa: E712
    c["LapTime_s"] = c["LapTime"].dt.total_seconds()
    fastest = c.groupby("race_id")["LapTime_s"].transform("min")
    c = c[c["LapTime_s"] <= 1.07 * fastest]
    c["FreshTyre"] = c["FreshTyre"].astype(bool)
    laps_clean = c[KEEP_LAPS].copy()
    laps_clean.to_parquet(os.path.join(DATA, f"{LAPS_OUT}.parquet"), index=False)

    # driver x race: grid 0 (pit-lane start) becomes the race's last grid slot + 1
    dr = res_raw.rename(columns={"Abbreviation": "Driver", "TeamName": "Team"})
    dr["GridPosition"] = dr["GridPosition"].replace(0, np.nan)
    dr["GridPosition"] = dr["GridPosition"].fillna(
        dr.groupby("race_id")["GridPosition"].transform("max") + 1
    )
    dr = dr[dr["Position"].notna()].copy()
    dr["podium"] = (dr["Position"] <= 3).astype(int)
    cols = [
        "Season",
        "Round",
        "EventName",
        "race_id",
        "Driver",
        "Team",
        "GridPosition",
        "Position",
        "Points",
        "Status",
        "quali_gap_s",
        "podium",
    ]
    dr = dr[cols]
    dr.to_parquet(os.path.join(DATA, f"{DR_OUT}.parquet"), index=False)

    print(f"\n{LAPS_OUT}: {laps_clean.shape} | {DR_OUT}: {dr.shape}")
    print(f"quali_gap_s non-null: {dr['quali_gap_s'].notna().sum()}/{len(dr)}")
    print(
        f"podium rate: {dr['podium'].mean():.3f} | podiums: {int(dr['podium'].sum())}"
    )


if __name__ == "__main__":
    main()
