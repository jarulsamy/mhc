#!/usr/bin/env python3
r"""
 __  __  _   _   ____
|  \/  || | | | / ___|
| |\/| || |_| || |
| |  | ||  _  || |___
|_|  |_||_| |_| \____|

Mental Health Calendar

  Keep track of your mental health
  without ever leaving your terminal

Default save location:
    $HOME/.config/mhc/

Files:
    cal.db - persistent storage of calendar data
    config.yaml - config file
"""
import datetime
import os
import random
from pathlib import Path

from cal import Calendar
from db import Database
from docopt import docopt


def get_rating(day="your day"):
    while True:
        try:
            rating = int(input(f"How was {day} (-3 (worst) to 3 (best)): "))
            break
        except ValueError:
            print("Invalid input")
    return rating


CLI = """

MCH - Mental Health Calendar

Keep track of oyour mental health
without every leaving your terminal.

Usage:
    mhc
    mhc view [--start=<date>] [--end=<date>]
    mhc [--edit=<date>]
    mhc [--redo]

Options:
    -h --help         Show this help.
    --version         Show version.
    --start<date>     Specify the start day for the calendar (MM-DD-YYYY)
    --end=<date>      Specify the end date for the calendar (MM-DD-YYYY)
    --edit<date>      Change a previous entry at day <date> (MM-DD-YYYY)
    --redo            Change todays entry
"""


DIR = Path(Path.home(), ".config", "mhc")
DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(DIR, "mhc.db")
QUOTE_PATH = Path(DIR, "quotes.txt")

db = Database(str(DB_PATH))

args = docopt(CLI)
if args.get("--edit") is not None:
    try:
        day = datetime.datetime.strptime(args.get("--edit"), "%m-%d-%Y").date()
    except ValueError as e:
        raise ValueError("Incorrect date format, must be MM-DD-YYYY") from e
    rating = get_rating(day)
    db.insert(day, rating)

elif args.get("--redo"):
    rating = get_rating()
    db.insert(datetime.date.today(), rating)

elif args.get("view"):
    start_date = None
    end_date = None

    if args.get("--start") is not None:
        try:
            start_date = datetime.datetime.strptime(
                args.get("--start"), "%m-%d-%Y"
            ).date()
        except ValueError as e:
            raise ValueError("Incorrect date format, must be MM-DD-YYYY") from e

    if args.get("--end") is not None:
        try:
            end_date = datetime.datetime.strptime(args.get("--end"), "%m-%d-%Y").date()
        except ValueError as e:
            raise ValueError("Incorrect date format, must be MM-DD-YYYY") from e
    cal = Calendar(db, start_date=start_date, end_date=end_date)
    print(str(cal))

else:
    if not db.find(datetime.date.today()):
        rating = get_rating()
        db.insert(datetime.date.today(), rating)
    else:
        print("You've already entered a day rating today.")

    try:
        with open(QUOTE_PATH, "r") as f:
            quotes = f.read().split("\n.")

        print("\n" + random.choice(quotes).strip() + "\n")
    except FileNotFoundError:
        pass
