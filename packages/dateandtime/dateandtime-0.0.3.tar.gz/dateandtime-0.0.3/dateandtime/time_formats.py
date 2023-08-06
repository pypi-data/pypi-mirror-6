"""Support for different calendaring methods."""


import calendar
import datetime
from ddate.base import DDate

from dateandtime import ANSI


def get_calendar(discordian=False):
    """Buffer for selecting the correct calendar.

    Returns:
        tuple of (calendar month text list, date object used to create it)
    """

    if discordian:
        date = DDate()
        cal =  discordian_calendar(date)
    else:
        date = datetime.datetime.now()
        # the TextCalendar(6) is to start the week on Sunday
        cal = calendar.TextCalendar(6).formatmonth(
            date.year,
            date.month,
        ).splitlines()[2:]

    return (cal, date)


def calendar_header(date):
    """"Get the month/year and weekday abbreviates for the date object."""

    # DDate time objects will have SEASONS defined
    if hasattr(date, "SEASONS"):
        weekday_abbrs = [day[:2].title() for day in date.WEEKDAYS]
        return date.SEASONS[date.season], date.day_of_season, weekday_abbrs
    else:
        weekday_abbrs = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        return date.strftime("%B"), date.strftime("%d"), weekday_abbrs


def discordian_calendar(date):
    """Simulate calendar.TextCalendar for discordian dates."""

    first_day_of_season = DDate(
        datetime.date(
            year=date.date.year,
            month=date.date.month,
            day=date.date.day,
        ) - datetime.timedelta(days=date.day_of_season - 1),
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


def get_next_days_of_next_month(line, discordian=False):
    """Fill in trailing whitespace with ansi-formatted dates for next month."""

    day = 0
    while len(line) < (5 if discordian else 7):
        day += 1
        line.append("{start}{date}{end}".format(
            start=ANSI.OTHERMONTH,
            date=str(day).rjust(2),
            end=ANSI.END,
        ))
    return line


def get_last_days_of_last_month(line, discordian=False):
    """Fill in leading whitespace with ansi-formatted dates from last month."""

    if discordian:
        day = 73
        max_len = 5
    else:
        day = 31
        now = datetime.datetime.now()
        lastmonth = now.month - 1 or 12
        lastmonthyear = now.year - (now.month - 1 == 0)
        max_len = 7

    while len(line) < max_len:
        try:
            if not discordian:
                datetime.datetime(year=lastmonthyear, month=lastmonth, day=day)
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
