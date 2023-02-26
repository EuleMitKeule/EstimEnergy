

def get_days_in_month(month: int, year: int):
    """Return the number of days in a given month and year."""
    if month == 2:
        # Check for leap years
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29
        else:
            return 28
    elif month in {4, 6, 9, 11}:
        return 30
    else:
        return 31