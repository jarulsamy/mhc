import dataset
import datetime
import random


class Database:
    def __init__(self, filename: str):
        self._db = dataset.connect(f"sqlite:///{filename}")
        self._table = self._db["calendar"]

    def insert(self, day, rating):
        if not isinstance(day, datetime.date):
            raise AttributeError("day must be datetime.date object")

        payload = {"date": day, "rating": rating}
        self._table.upsert(payload, ["date"])

    def dump(self):
        return self._table.all()

    def find(self, day):
        return self._table.find_one(date=day)

    def get_range(self, start_date, end_date):
        delta = end_date - start_date
        data = {}
        for i in range(delta.days + 1):
            new_date = start_date + datetime.timedelta(days=i)
            try:
                data[new_date] = self.find(new_date).get("rating")
            except AttributeError:
                data[new_date] = None

        return data


def random_date():
    """Get a random date between 1900 and today"""

    min_year = 1900
    max_year = datetime.datetime.now().year

    start = datetime.date(min_year, 1, 1)
    years = max_year - min_year + 1
    end = start + datetime.timedelta(days=365 * years)
    return start + (end - start) * random.random()
