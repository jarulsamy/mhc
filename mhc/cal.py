import datetime
import db


def pad_end(text, pad_char, max_len, start=None, end=None):
    final = ""
    if start is not None:
        final += start

    final += text + (str(pad_char) * max_len)

    if end is not None:
        final += end

    return final + "\n"


class Calendar:
    def __init__(self, db: db.Database, start_date: datetime.date = None, end_date: datetime.date = None):
        self._db = db
        self._start_date = start_date
        self._end_date = end_date

        # One year range by default
        if not self._end_date:
            self._end_date = datetime.date.today()
        if not self._start_date:
            self._start_date = self._end_date - datetime.timedelta(days=365)

        self.colors = ("#691A1A", "#9F1E1E", "#C9231A", "#E6E620", "#4A8C19", "#47CB21", "#53FF00")

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @start_date.setter
    def start_date(self, new_date):
        try:
            self._start_date = datetime.datetime.strptime("%m-%d-%Y")
        except ValueError as e:
            raise ValueError("Incorrect date format, should be MM-DD-YYYY") from e

    @end_date.setter
    def end_date(self, new_date):
        try:
            self._end_date = datetime.datetime.strptime("%m-%d-%Y")
        except ValueError as e:
            raise ValueError("Incorrect date format, should be MM-DD-YYYY") from e

    def _colored(self, color_hex, text):
        color_hex = color_hex.lstrip("#")
        r, g, b = tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    def color_test(self):
        """Print a color spectrum to check if the terminal supports all the colors"""
        for i in self.colors:
            print(f"{i}: {self._colored(i, '◼')}")
        print(f"If you can see all {len(self.colors)} colors, your terminal is working correctly")

    def __str__(self):
        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        marks = {"nw": "╔", "n": "═", "ne": "╗", "e": "║", "se": "╝", "s": "═", "sw": "╚", "w": "║", "b": " "}
        # Extra symbols: ["⬚", "▢", "▤", "▣", "◼"]
        full_marker = "◼"
        empty_marker = "⬚"

        self._data = self._db.get_range(self._start_date, self._end_date)

        current_date = self.start_date - datetime.timedelta((self.start_date.weekday() + 1) % 7)
        num_weeks, leftover_days = divmod(abs(self.end_date - current_date).days, 7)
        if leftover_days > 0:
            num_weeks += 1

        cols = [days_of_week]
        month_str = "  "

        # Process the days week by week
        for w in range(num_weeks):
            week = []
            for i in range(7):
                # pretty_date = datetime.datetime.strftime(current_date, "%m/%d")
                # Print empty space for padding days
                if current_date < self.start_date or current_date > self.end_date:
                    week.append(marks["b"])
                else:
                    rating = self._data.get(current_date)
                    # Draw with appropiate color values
                    if rating is not None:
                        if rating <= -3:
                            week.append(self._colored(self.colors[0], full_marker))
                        elif rating >= 3:
                            week.append(self._colored(self.colors[-1], full_marker))
                        else:
                            week.append(self._colored(self.colors[rating + 3], full_marker))
                    else:
                        week.append(empty_marker)

                current_date += datetime.timedelta(days=1)

            if current_date.day >= 0 and current_date.day <= 7:
                month_str += months[current_date.month - 1]
            elif current_date.day > 7:
                month_str += "  "

            cols.append(week)

        month_line = month_str.rstrip()

        # ╔════════════╗
        # ║Sun ⬚ ⬚ ⬚ ◼ ║
        # ║Mon ⬚ ⬚ ⬚ ◼ ║
        # ║Tue ⬚ ⬚ ⬚ ◼ ║
        # ║Wed ⬚ ⬚ ⬚ ◼ ║
        # ║Thu ⬚ ⬚ ⬚ ◼ ║
        # ║Fri ⬚ ⬚ ◼   ║
        # ║Sat ⬚ ⬚ ◼   ║
        # ║------------║
        # ║ Start  End ║
        # ╚════════════╝

        data_lines = []
        for i in range(7):
            temp_line = ""
            data_len = 0
            for j in range(len(cols)):
                temp_line += str(cols[j][i]) + " "
                data_len += 2
            data_lines.append(temp_line)

        start_end_line = (
            f"Start date: {self.start_date.strftime('%m/%d/%Y')} | End date: {self.end_date.strftime('%m/%d/%Y')}"
        )

        # Get the max width to keep the size of the box consistent
        max_width = len(max((month_line, " " * (data_len + 3), start_end_line), key=len))

        # Assemble the final output by combining all the previous lines
        # and padding them appropiately
        output = pad_end("", marks["n"], max_width, marks["nw"], marks["ne"])
        output += pad_end(month_line, " ", max_width - len(month_line), marks["w"], marks["w"])

        for i in data_lines:
            # HACK: -2 for some reason needs to be there to get spacing correct
            output += pad_end(i, " ", max_width - data_len - 2, marks["w"], marks["w"])

        output += pad_end("", "-", (max_width), marks["w"], marks["w"])
        output += pad_end(start_end_line, " ", (max_width - len(start_end_line)), marks["w"], marks["w"])
        output += marks["sw"] + (marks["n"] * (max_width)) + marks["se"] + "\n"

        return output
