from calcrule_validations.strategies.base_strategy import BaseValidationsStrategy
from calcrule_validations.strategies.parameter_helpers import is_blank, number_parameter, result, to_number


class NumberRangeValidationStrategy(BaseValidationsStrategy):
    """The value is a number from ``min`` to ``max``, both inclusive; either may be left out."""
    VALIDATION_CLASS = "NumberRangeValidationStrategy"

    @classmethod
    def validate(cls, field_name, field_value, **kwargs):
        (minimum, min_error), (maximum, max_error) = number_parameter(kwargs, "min"), number_parameter(kwargs, "max")
        if min_error or max_error:
            return result(field_name, False, min_error or max_error)
        if minimum is None and maximum is None:
            return result(field_name, False, "No min or max configured")
        if is_blank(field_value):
            return result(field_name, False, "No value")
        number = to_number(field_value)
        if number is None:
            return result(field_name, False, f"'{field_value}' is not a number")
        if minimum is not None and number < minimum:
            return result(field_name, False, f"{field_value} is less than {minimum}")
        if maximum is not None and number > maximum:
            return result(field_name, False, f"{field_value} is more than {maximum}")
        return result(field_name, True)
