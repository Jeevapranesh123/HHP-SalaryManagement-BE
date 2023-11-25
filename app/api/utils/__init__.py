import datetime


def first_day_of_current_month():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, 1, 0, 0, 0)


def last_day_of_current_month():
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    if ((year % 400 == 0) and (year % 100 == 0)) or (
        (year % 4 == 0) and (year % 100 != 0)
    ):
        if month == 2:
            return datetime.datetime(year, month, 29, 0, 0, 0)

    if 1 <= month <= 7:
        if month == 2:
            return datetime.datetime(year, month, 28, 0, 0, 0)
        if month % 2 == 0:
            return datetime.datetime(year, month, 30, 0, 0, 0)
        else:
            return datetime.datetime(year, month, 31, 0, 0, 0)

    else:
        if month % 2 == 0:
            return datetime.datetime(year, month, 31, 0, 0, 0)
        else:
            return datetime.datetime(year, month, 30, 0, 0, 0)
