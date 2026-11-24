from datetime import date, datetime

from django.test import SimpleTestCase

from calcrule_validations.strategies import ValidationStrategyStorage
from calcrule_validations.strategies.parameter_helpers import to_date

ON = "2026-11-23T08:30:00Z"


def check(name, value, **params):
    outcome = ValidationStrategyStorage.choose_strategy(name).validate("answer", value, **params)
    return outcome["success"], outcome["note"]


class StrategyLookupTest(SimpleTestCase):
    def test_strategies_are_found_by_name(self):
        for name in ("ValueInListValidationStrategy", "NumberRangeValidationStrategy", "AgeRangeValidationStrategy",
                     "DateAfterValidationStrategy", "RegexValidationStrategy", "EmailValidationStrategy"):
            with self.subTest(name=name):
                self.assertEqual(ValidationStrategyStorage.choose_strategy(name).VALIDATION_CLASS, name)

    def test_a_result_names_the_field(self):
        outcome = ValidationStrategyStorage.choose_strategy("RegexValidationStrategy").validate(
            "national_id", "AB12CD34", pattern="^[A-Z0-9]{8}$")
        self.assertEqual(outcome, {"success": True, "field_name": "national_id", "note": "Ok", "duplications": None})


class ValueInListTest(SimpleTestCase):
    def test_values(self):
        values = ["jce", "msce", 7]
        cases = [("msce", True), (" jce ", True), ("JCE", False), ("pslc", False), (7, True), ("7", True)]
        for value, success in cases:
            with self.subTest(value=value):
                self.assertEqual(check("ValueInListValidationStrategy", value, values=values)[0], success)

    def test_blank_and_unconfigured(self):
        self.assertEqual(check("ValueInListValidationStrategy", "", values=["a"]), (False, "No value"))
        self.assertEqual(check("ValueInListValidationStrategy", "a"), (False, "No values configured to check against"))


class NumberRangeTest(SimpleTestCase):
    def test_bounds_are_inclusive(self):
        cases = [(3000000, True), ("3000000", True), ("3,500,000", True), (2999999.99, False), (5000000, True),
                 (5000000.01, False), ("abc", False), (True, False)]
        for value, success in cases:
            with self.subTest(value=value):
                self.assertEqual(check("NumberRangeValidationStrategy", value, min=3000000, max=5000000)[0], success)

    def test_one_bound_is_enough(self):
        self.assertTrue(check("NumberRangeValidationStrategy", 10 ** 9, min=3000000)[0])
        self.assertEqual(check("NumberRangeValidationStrategy", 1), (False, "No min or max configured"))

    def test_non_finite_values_fail(self):
        for value in ("nan", "NaN", "inf", "-inf", float("inf"), "1e999"):
            with self.subTest(value=value):
                self.assertEqual(check("NumberRangeValidationStrategy", value, min=3000000),
                                 (False, f"'{value}' is not a number"))
        # A float NaN is an empty cell in a pandas-read upload
        self.assertEqual(check("NumberRangeValidationStrategy", float("nan"), min=3000000), (False, "No value"))

    def test_a_bound_that_is_not_a_number_fails_with_a_note(self):
        for params in ({"min": "18"}, {"max": True}, {"min": 1, "max": float("nan")}):
            with self.subTest(params=params):
                success, note = check("NumberRangeValidationStrategy", 20, **params)
                self.assertFalse(success)
                self.assertIn("is not a number", note)


class AgeRangeTest(SimpleTestCase):
    def test_completed_years_on_the_reference_date(self):
        cases = [("2008-11-23", True), ("2008-11-24", False), ("1990-11-24", True), ("1990-11-23", False),
                 (date(2000, 1, 1), True), (datetime(2000, 1, 1, 12), True)]
        for dob, success in cases:
            with self.subTest(dob=dob):
                self.assertEqual(check("AgeRangeValidationStrategy", dob, min=18, max=35, reference_date=ON)[0],
                                 success)

    def test_notes(self):
        self.assertEqual(check("AgeRangeValidationStrategy", "1990-11-23", min=18, max=35, reference_date=ON),
                         (False, "Aged 36 on 2026-11-23, over 35"))
        self.assertEqual(check("AgeRangeValidationStrategy", "2030-01-01", min=18, reference_date=ON)[1],
                         "Date of birth 2030-01-01 is after 2026-11-23")
        self.assertEqual(check("AgeRangeValidationStrategy", "soon", min=18), (False, "'soon' is not a date"))
        self.assertEqual(check("AgeRangeValidationStrategy", "2000-01-01", min="18"),
                         (False, "Configured min '18' is not a number"))


class DateAfterTest(SimpleTestCase):
    def test_on_or_after_the_reference_date(self):
        cases = [("2026-11-23", True), ("2027-01-01", True), ("2026-11-22", False), ("never", False), ("", False)]
        for value, success in cases:
            with self.subTest(value=value):
                self.assertEqual(check("DateAfterValidationStrategy", value, reference_date=ON)[0], success)

    def test_default_reference_is_today(self):
        self.assertTrue(check("DateAfterValidationStrategy", date.today())[0])


class RegexTest(SimpleTestCase):
    def test_whole_value_must_match(self):
        cases = [("AB12CD34", True), (" AB12CD34 ", True), ("AB12CD345", False), ("AB12-D34", False)]
        for value, success in cases:
            with self.subTest(value=value):
                self.assertEqual(check("RegexValidationStrategy", value, pattern="^[A-Za-z0-9]{8}$")[0], success)

    def test_bad_or_missing_pattern(self):
        self.assertFalse(check("RegexValidationStrategy", "x", pattern="(")[0])
        self.assertEqual(check("RegexValidationStrategy", "x"), (False, "No pattern configured"))


class ToDateTest(SimpleTestCase):
    def test_formats(self):
        for value in ("2026-11-23", "2026-11-23T08:30:00", ON, "2026-11-23T08:30:00.123+02:00",
                      date(2026, 11, 23), datetime(2026, 11, 23, 8)):
            with self.subTest(value=value):
                self.assertEqual(to_date(value), date(2026, 11, 23))
        for value in ("23/11/2026", "2026-11-23garbage", "2026-11-23 and more", "2026-02-30", "2026-11-23T"):
            with self.subTest(value=value):
                self.assertIsNone(to_date(value))
