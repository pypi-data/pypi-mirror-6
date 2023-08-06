"""A little clock to tell the date & time."""


import time
import datetime

from dateandtime.multicalendar import MultiCalendar


def be_a_clock(discordian=False, eve_real=False, eve_game=False, test=False):
    """Displays a calendar with the day highlighted, a blank line and the time
    of day. Will loop forever. Sends many blank lines during a day change to
    badly update the highlighted day.
    """

    while True:
        starting_time = datetime.datetime.now()
        running_time = starting_time
        calendar = MultiCalendar(discordian, eve_real, eve_game)
        calendar.print_spaces()
        calendar.print_calendar()
        while starting_time.day == running_time.day:
            calendar.print_time(running_time)
            printed_time = running_time
            while printed_time.minute == running_time.minute:
                running_time = datetime.datetime.now()
                time.sleep(1)
                if test:
                    return  # short circut to make this function testable


def parse_args(args=None):
    """Lazy argument parsing...

    Arguments:
        args: a list of strings to search through

    Returns:
        dict of kwargs suitable for be_a_clock

    Raises:
        SystemExit when supplying too many matching arguments
    """

    possible_args = [
        ("discordian", ["-d", "--discord", "--discordian", "--discordianism"]),
        ("eve_game", ["-e", "--eve", "--eve-game"]),
        ("eve_real", ["-r", "--eve-real", "--eve-is-real"]),
        ("help", ["-h", "--help"]),
    ]

    requested = dict((cal, False) for cal, _ in possible_args)

    for arg in args or []:
        for calendar, arg_flags in possible_args:
            if arg in arg_flags:
                requested[calendar] = True

    if requested["help"]:
        raise SystemExit((
            "Dateandtime usage:\n  dateandtime [calendar] [-h/--help]\n"
            "Alternate calendars (usage flags):\n  {0}".format(
                "\n  ".join(
                    "{0}{1}{2}{3}: [{4}]".format(
                        name.split("_")[0].title(),
                        " (" * int("_" in name),
                        " ".join(name.split("_")[1:]),
                        ")" * int("_" in name),
                        ", ".join(flags),
                    )
                    for name, flags in possible_args[:-1]
                )
            )
        ))

    if sum(requested.values()) > 1:
        requested_cals = [
            cal.replace("_", " ") for cal, _ in possible_args if requested[cal]
        ]
        raise SystemExit((
            "Please limit yourself to a single calendar.\n"
            "I cannot display {0} and {1} at the same time {2}"
        ).format(
            ", ".join(requested_cals[:-1]),
            requested_cals[-1],
            ":/" if len(requested_cals) < 3 else ":(",
        ))

    requested.pop("help")
    return requested
