import re

from calcrule_validations.strategies.base_strategy import BaseValidationsStrategy
from calcrule_validations.strategies.parameter_helpers import is_blank, result


class RegexValidationStrategy(BaseValidationsStrategy):
    """The whole value (as text, surrounding spaces ignored) matches the regular expression ``pattern``."""
    VALIDATION_CLASS = "RegexValidationStrategy"

    @classmethod
    def validate(cls, field_name, field_value, **kwargs):
        pattern = kwargs.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            return result(field_name, False, "No pattern configured")
        if is_blank(field_value):
            return result(field_name, False, "No value")
        try:
            matched = re.fullmatch(pattern, str(field_value).strip())
        except re.error as exc:
            return result(field_name, False, f"Invalid pattern: {exc}")
        return result(field_name, True) if matched else result(field_name, False, "Not in the expected format")
