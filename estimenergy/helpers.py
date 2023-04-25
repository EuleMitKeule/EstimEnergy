"""Helper functions."""


def get_days_in_month(month: int, year: int):
    """Return the number of days in a given month and year."""

    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29

        return 28

    if month in {4, 6, 9, 11}:
        return 30

    return 31


def get_days_in_year(year: int):
    """Return the number of days in a given year."""

    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return 366

    return 365
