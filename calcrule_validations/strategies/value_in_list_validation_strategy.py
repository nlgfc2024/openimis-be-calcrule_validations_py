from calcrule_validations.strategies.base_strategy import BaseValidationsStrategy
from calcrule_validations.strategies.parameter_helpers import is_blank, result


class ValueInListValidationStrategy(BaseValidationsStrategy):
    """The value is one of ``values`` (compared as text, case-sensitive, surrounding spaces ignored)."""
    VALIDATION_CLASS = "ValueInListValidationStrategy"

    @classmethod
    def validate(cls, field_name, field_value, **kwargs):
        values = kwargs.get("values")
        if not isinstance(values, (list, tuple)) or not values:
            return result(field_name, False, "No values configured to check against")
        if is_blank(field_value):
            return result(field_name, False, "No value")
        allowed = {str(value).strip() for value in values}
        if str(field_value).strip() in allowed:
            return result(field_name, True)
        return result(field_name, False, f"'{field_value}' is not one of: {', '.join(map(str, values))}")
