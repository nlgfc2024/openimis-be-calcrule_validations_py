"""Value parsing and results shared by the parameterised strategies (value in list, number range, age range,
date after, regex). Their parameters come as keyword arguments; a missing parameter is a failed validation that
says which, not an exception."""
import math
import re
from dataclasses import asdict
from datetime import date, datetime

from calcrule_validations.strategies.validation_strategy_interface import ValidationResult


def result(field_name, success, note="Ok"):
    return asdict(ValidationResult(success=success, field_name=field_name, note=note))


# An ISO date, optionally followed by a time and offset, and nothing else
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}(:?\d{2})?)?)?")


def is_blank(value):
    """None, empty text or NaN (an empty cell in a pandas-read upload)."""
    if isinstance(value, float) and math.isnan(value):
        return True
    return value is None or (isinstance(value, str) and not value.strip())


def to_number(value):
    """A finite number from an int, float or numeric text ("3,500,000" too); None otherwise ("nan", "inf")."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value) if isinstance(value, (int, float)) else float(str(value).replace(",", "").strip())
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def number_parameter(kwargs, name):
    """A configured number parameter: (value, None), (None, None) when left out, or (None, note) when not a
    finite number, so a ``"18"`` from JSON fails with a note rather than a TypeError."""
    value = kwargs.get(name)
    if value is None:
        return None, None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None, f"Configured {name} '{value}' is not a number"
    return value, None


def to_date(value):
    """A date from a date, a datetime or ISO text ("2026-11-18", "2026-11-18T08:00:00Z"); None otherwise."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        text = value.strip()
        if not ISO_DATE.fullmatch(text):
            return None
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    return None


def reference_date(kwargs):
    """The ``reference_date`` keyword argument as a date (default: today), or None when it can't be read."""
    if kwargs.get("reference_date") is None:
        return date.today()
    return to_date(kwargs["reference_date"])


def completed_years(born, on):
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))
