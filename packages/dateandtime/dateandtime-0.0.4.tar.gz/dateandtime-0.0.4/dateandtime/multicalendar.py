"""Output formatting for dateandtime."""


from __future__ import print_function

import sys
import calendar
import datetime
from ddate.base import DDate


class ANSI(object):
    """ANSI terminal colour settings."""

    TODAY = "\033[94m"
    PAST = "\033[31m"
    OTHERMONTH = "\033[36m"
    END = "\033[0m"


class MultiCalendar(object):
    """Prints multiple types of calendars."""

    def __init__(self, discordian=False, eve_real=False, eve_game=False):
        self.discordian = discordian
        self.eve_real = eve_real
        self.eve_game = eve_game

        if self.discordian:
            self.max_width = 14
            self.date = DDate()
            self.calendar = self.discordian_calendar()
            self.month = self.date.SEASONS[self.date.season]
            self.ending_days = ["70", "71", "72", "73"]
            self.day_of_month = self.date.day_of_season
            self.weekday_abbrs = [d[:2].title() for d in self.date.WEEKDAYS]
        else:
            self.max_width = 20
            self.date = datetime.datetime.now()
            self.month = self.date.strftime("%B")
            # start the week on Sunday
            self.calendar = calendar.TextCalendar(6).formatmonth(
                self.date.year,
                self.date.month,
            ).splitlines()[2:]
            self.ending_days = ["28", "29", "30", "31"]
            self.day_of_month = self.date.strftime("%d")
            self.weekday_abbrs = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

        if self.eve_real:
            self.year = 23236 + (self.date.year - 1900)
        elif self.eve_game:
            self.year = "YC {0}".format(self.date.year - 1900)
        else:
            self.year = self.date.year

    def print_calendar(self):
        """Prints the calendar, highlights the day."""

        tag_line = "{0} {1}".format(self.month, self.year)

        if len(tag_line) > self.max_width:
            tag_line = "{0} {1}".format(
                self.month[:3],
                self.year,
            )

        print(tag_line.center(self.max_width, " "))
        print(" ".join(self.weekday_abbrs))

        first_day = True
        for line in self.calendar:
            formatted_days = []
            for day in line.split():
                if int(day) == int(self.day_of_month):
                    formatted_days.append("{end}{start}{day}{end}".format(
                        start=ANSI.TODAY,
                        day=str(day).rjust(2),
                        end=ANSI.END,
                    ))
                    first_day = False
                else:
                    if first_day:
                        first_day = False
                        formatted_days.append("{start}{day}".format(
                            start=ANSI.PAST,
                            day=str(day).rjust(2),
                        ))
                    else:
                        formatted_days.append(str(day).rjust(2))
            print("{line}".format(line=self.format_line(formatted_days)))
        print("")

    def print_spaces(self):
        """Prints a bunch of spaces..."""

        print("\n".join([" " * self.max_width for _ in range(420)]))

    def format_line(self, line):
        """For a line of a calendar, replace any whitespace with the next or
        previous month's dates.

        Args:
            line: the list of formatted days

        Returns:
            line, joined by spaces, including the other month's formatted dates
        """

        if len(line) < 5 if self.discordian else 7:
            first_week = True
            for day in line:
                for ending_day in self.ending_days:
                    if ending_day == day:
                        first_week = False
                    elif day.endswith("{0}{1}".format(ending_day, ANSI.END)):
                        first_week = False

            if first_week:
                return "{line}".format(
                    line=" ".join(
                        self.get_last_days_of_last_month(line))
                )
            else:
                return "{line}".format(
                    line=" ".join(self.get_next_days_of_next_month(line))
                )
        else:
            return " ".join(line)

    def print_time(self, now):
        """Prints the time line.

        Args:
            now: a datetime.now() object
        """

        print(
            "\r{time}".format(time="{hour}:{minute} {ampm}".format(
                hour=int(now.strftime("%I")),
                minute=now.strftime("%M"),
                ampm=now.strftime("%p").lower(),
            ).center(self.max_width, " ")),
            end="",
        )
        sys.stdout.flush()

    def get_next_days_of_next_month(self, line):
        """Fill in trailing whitespace with formatted dates for next month."""

        day = 0
        while len(line) < (5 if self.discordian else 7):
            day += 1
            line.append("{start}{date}{end}".format(
                start=ANSI.OTHERMONTH,
                date=str(day).rjust(2),
                end=ANSI.END,
            ))
        return line

    def get_last_days_of_last_month(self, line, now=None):
        """Fill in leading whitespace with formatted dates from last month."""

        if self.discordian:
            day = 73
            max_len = 5
        else:
            day = 31
            now = now or datetime.datetime.now()
            lastmonth = now.month - 1 or 12
            lastmonthyear = now.year - (now.month - 1 == 0)
            max_len = 7

        while len(line) < max_len:
            try:
                if not self.discordian:
                    datetime.datetime(
                        year=lastmonthyear,
                        month=lastmonth,
                        day=day,
                    )
            except ValueError:
                pass
            else:
                line.insert(0, "{start}{date}{end}".format(
                    start=ANSI.OTHERMONTH,
                    date=str(day).rjust(2),
                    end=ANSI.END,
                ))
            finally:
                day -= 1
        return line

    def discordian_calendar(self):
        """Simulate calendar.TextCalendar for discordian dates."""

        first_day_of_season = DDate(
            datetime.date(
                year=self.date.date.year,
                month=self.date.date.month,
                day=self.date.date.day,
            ) - datetime.timedelta(days=self.date.day_of_season - 1),
        )

        weeks = []
        first_week = True

        start_day = first_day_of_season.day_of_week
        for week in range(1, 77, 5):
            if first_week:
                weeks.append("{0}{1}".format(
                    "  " * start_day,
                    " ".join([str(x).rjust(2, " ") for x in range(
                        1, 6 - start_day)]
                    ),
                ))
                first_week = False
            else:
                weeks.append(" ".join(
                    [str(x) for x in range(
                        week - start_day, min((week - start_day) + 5, 74))]
                ))

        return weeks
