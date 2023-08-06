"""Output formatting for dateandtime."""


import sys

from dateandtime import ANSI
from dateandtime.time_formats import (
    calendar_header,
    get_calendar,
    get_last_days_of_last_month,
    get_next_days_of_next_month,
)


def print_spaces():
    """Prints a bunch of spaces..."""

    for _ in xrange(420):
        print("{newlines}".format(newlines="\n" * 10))


def print_calendar(discordian=False, eve_real=False, eve_game=False):
    """Prints the calendar, highlights the day."""

    this_month, date = get_calendar(discordian)

    if eve_real:
        year = 23236 + (date.year - 1900)
    elif eve_game:
        year = "YC {0}".format(date.year - 1900)
    else:
        year = date.year

    month, day_of_month, weekday_abbrs = calendar_header(date)

    tag_line = "{0} {1}".format(month, year)
    if discordian:
        max_width = 14
    else:
        max_width = 20

    if len(tag_line) > max_width:
        tag_line = "{0} {1}".format(month[:3], date.year)

    print("{0}{1}\n{2}".format(
        " " * ((max_width - len(tag_line)) / 2),
        tag_line,
        " ".join(weekday_abbrs),
    ))

    first_day = True
    for line in this_month:
        formatted_days = []
        for day in line.split():
            if int(day) == int(day_of_month):
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
        print("{line}".format(line=format_line(formatted_days, discordian)))


def print_time(now, discordian=False):
    """Prints the time line.

    Args:
        now: a datetime.now() object
    """

    if discordian:
        tab = 3
        tail = 2
    else:
        tab = 6
        tail = 5

    sys.stdout.write("\r{tab}{hour}:{minute} {ampm}{tail}".format(
        tab=" " * (tab + (1 * (int(now.strftime("%I")) < 10))),
        hour=int(now.strftime("%I")),
        minute=now.strftime("%M"),
        ampm=now.strftime("%p").lower(),
        tail=" " * tail,
    ))
    sys.stdout.flush()


def format_line(line, discordian=False):
    """For a line of a calendar, replace any whitespace with the next or
    previous month's dates.

    Args:
        line: the list of formatted days

    Returns:
        line, joined by spaces, including the other month's formatted dates
    """

    if len(line) < 7:
        first_week = True
        if discordian:
            ending_days = ["70", "71", "72", "73"]
        else:
            ending_days = ["28", "29", "30", "31"]
        for day in line:
            for ending_day in ending_days:
                if ending_day == day:
                    first_week = False
                elif day.endswith("{0}{1}".format(ending_day, ANSI.END)):
                    first_week = False

        if first_week:
            return "{line}".format(
                line=" ".join(get_last_days_of_last_month(line, discordian)),
            )
        else:
            return "{line}".format(
                line=" ".join(get_next_days_of_next_month(line, discordian)),
            )
    else:
        return " ".join(line)
