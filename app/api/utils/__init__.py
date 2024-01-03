import datetime
import openpyxl.utils


def first_day_of_current_month(month=None, year=None):
    now = datetime.datetime.now()
    if month and year:
        return datetime.datetime(year, month, 1, 0, 0, 0)
    return datetime.datetime(now.year, now.month, 1, 0, 0, 0)


def first_day_of_last_month(month=None, year=None):
    now = datetime.datetime.now()

    if month and year:
        return datetime.datetime(year, month, 1)

    # Check if the current month is January
    if now.month == 1:
        # Set the month to December and decrement the year
        return datetime.datetime(now.year - 1, 12, 1)
    else:
        # Otherwise, just decrement the month
        return datetime.datetime(now.year, now.month - 1, 1)


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


def last_day_of_last_month():
    now = datetime.datetime.now()
    month = now.month - 1
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


def get_next_month(month, year):
    if month == 12:
        return 1, year + 1
    return month + 1, year


def adjust_column_widths(worksheet):
    for column in worksheet.columns:
        max_length = 0
        column_cells = [cell for cell in column if cell.value is not None]

        if not column_cells:
            continue  # Skip empty columns

        for cell in column_cells:
            try:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length
            except:
                pass

        adjusted_width = max_length + 2  # Adding a little extra space for aesthetics
        worksheet.column_dimensions[
            openpyxl.utils.get_column_letter(column[0].column)
        ].width = adjusted_width
