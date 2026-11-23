from calcrule_validations.strategies.base_strategy import BaseValidationsStrategy
from calcrule_validations.strategies.parameter_helpers import is_blank, reference_date, result, to_date


class DateAfterValidationStrategy(BaseValidationsStrategy):
    """The value is a date on or after ``reference_date`` (default today), e.g. an expiry date that hasn't
    passed: a certificate expiring on the reference date is still valid that day."""
    VALIDATION_CLASS = "DateAfterValidationStrategy"

    @classmethod
    def validate(cls, field_name, field_value, **kwargs):
        if is_blank(field_value):
            return result(field_name, False, "No value")
        value, on = to_date(field_value), reference_date(kwargs)
        if value is None:
            return result(field_name, False, f"'{field_value}' is not a date")
        if on is None:
            return result(field_name, False, f"Reference date '{kwargs.get('reference_date')}' is not a date")
        if value < on:
            return result(field_name, False, f"{value} is before {on}")
        return result(field_name, True)
