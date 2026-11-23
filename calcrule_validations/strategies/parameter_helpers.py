"""Value parsing and results shared by the parameterised strategies (value in list, number range, age range,
date after, regex). Their parameters come as keyword arguments; a missing parameter is a failed validation that
says which, not an exception."""
from dataclasses import asdict
from datetime import date, datetime

from calcrule_validations.strategies.validation_strategy_interface import ValidationResult


def result(field_name, success, note="Ok"):
    return asdict(ValidationResult(success=success, field_name=field_name, note=note))


def is_blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def to_number(value):
    """A number from an int, float or numeric text ("3,500,000" too); None when it isn't one."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def to_date(value):
    """A date from a date, a datetime or ISO text ("2026-11-18", "2026-11-18T08:00:00Z"); None otherwise."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        text = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text).date()
        except ValueError:
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
