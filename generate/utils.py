import calendar
from collections import namedtuple
from typing import Any, Callable, Dict, Union

# helper types / type aliases
MonthDate = namedtuple("Date", ["year", "month"])
Data = Dict[str, Any]
FormattedFields = Dict[str, str]
Parser = Callable[[Data], Data]
Formatter = Callable[[Data], FormattedFields]


def parse_date(date: str) -> Union[MonthDate, str]:
    try:
        month, year = date.split()
        month = list(calendar.month_name).index(month.title())
        year = int(year)
        return MonthDate(year, month)
    except ValueError:
        return date


def format_date_long(date):
    return (
        f"{calendar.month_name[date.month]} {date.year}"
        if isinstance(date, MonthDate)
        else date
    )


def format_date_short(date):
    return (
        f"{calendar.month_name[date.month][:3]} {date.year}"
        if isinstance(date, MonthDate)
        else date
    )


def format_optional(optional):
    return optional if optional else ""
