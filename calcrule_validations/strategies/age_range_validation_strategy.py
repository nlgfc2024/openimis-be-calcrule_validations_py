from calcrule_validations.strategies.base_strategy import BaseValidationsStrategy
from calcrule_validations.strategies.parameter_helpers import (
    completed_years, is_blank, number_parameter, reference_date, result, to_date,
)


class AgeRangeValidationStrategy(BaseValidationsStrategy):
    """The value is a date of birth whose completed years on ``reference_date`` (default today) are from
    ``min`` to ``max``, both inclusive; either may be left out."""
    VALIDATION_CLASS = "AgeRangeValidationStrategy"

    @classmethod
    def validate(cls, field_name, field_value, **kwargs):
        (minimum, min_error), (maximum, max_error) = number_parameter(kwargs, "min"), number_parameter(kwargs, "max")
        if min_error or max_error:
            return result(field_name, False, min_error or max_error)
        if minimum is None and maximum is None:
            return result(field_name, False, "No min or max age configured")
        if is_blank(field_value):
            return result(field_name, False, "No value")
        born, on = to_date(field_value), reference_date(kwargs)
        if born is None:
            return result(field_name, False, f"'{field_value}' is not a date")
        if on is None:
            return result(field_name, False, f"Reference date '{kwargs.get('reference_date')}' is not a date")
        if born > on:
            return result(field_name, False, f"Date of birth {born} is after {on}")
        age = completed_years(born, on)
        if minimum is not None and age < minimum:
            return result(field_name, False, f"Aged {age} on {on}, under {minimum}")
        if maximum is not None and age > maximum:
            return result(field_name, False, f"Aged {age} on {on}, over {maximum}")
        return result(field_name, True, f"Aged {age} on {on}")
