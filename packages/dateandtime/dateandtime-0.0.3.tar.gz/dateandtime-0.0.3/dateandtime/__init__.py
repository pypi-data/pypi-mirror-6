"""Dateandtime package level imports."""


class ANSISettings(object):
    """ANSI terminal colour settings."""

    TODAY = "\033[94m"
    PAST = "\033[31m"
    OTHERMONTH = "\033[36m"
    END = "\033[0m"


ANSI = ANSISettings()
