"""
Tests for the calculator logic (Task 3, Step 5: test application functionality).

Run with:  py -m unittest -v
No extra libraries are needed.
"""

import unittest

from calculator_logic import (
    Calculator,
    CalculatorError,
    balance_parentheses,
    evaluate,
    format_number,
)


def press_keys(*keys):
    """Create a calculator, press the keys in order and return it."""
    calc = Calculator()
    for key in keys:
        calc.press(key)
    return calc


class TestEvaluate(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(evaluate("12+7"), 19)
        self.assertEqual(evaluate("10−4"), 6)
        self.assertEqual(evaluate("6×7"), 42)
        self.assertEqual(evaluate("9÷2"), 4.5)

    def test_order_of_operations(self):
        self.assertEqual(evaluate("2+3×4"), 14)
        self.assertEqual(evaluate("(2+3)×4"), 20)

    def test_negative_numbers(self):
        self.assertEqual(evaluate("−5×(−3)"), 15)

    def test_divide_by_zero(self):
        with self.assertRaisesRegex(CalculatorError, "divide by zero"):
            evaluate("5÷0")

    def test_invalid_expressions(self):
        for expression in ["5+", "×3", "2(3", "", "1..2"]:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    evaluate(expression)

    def test_code_cannot_be_run(self):
        """Typed input must never execute Python code (no eval)."""
        for expression in ["__import__('os')", "abs(5)", "2**3", "[1]", "True+1"]:
            with self.subTest(expression=expression):
                with self.assertRaises(CalculatorError):
                    evaluate(expression)

    def test_huge_results_are_rejected(self):
        with self.assertRaisesRegex(CalculatorError, "too large"):
            evaluate("1e200×1e200")


class TestFormatting(unittest.TestCase):
    def test_whole_numbers_have_no_decimal_point(self):
        self.assertEqual(format_number(8.0), "8")

    def test_floating_point_noise_is_hidden(self):
        self.assertEqual(format_number(evaluate("0.1+0.2")), "0.3")

    def test_long_decimals_are_rounded(self):
        self.assertEqual(format_number(2 / 3), "0.666666666667")

    def test_negative_numbers_use_display_minus(self):
        self.assertEqual(format_number(-5), "−5")

    def test_negative_zero(self):
        self.assertEqual(format_number(-0.0), "0")

    def test_balance_parentheses(self):
        self.assertEqual(balance_parentheses("2×(3+(4"), "2×(3+(4))")
        self.assertEqual(balance_parentheses("(1)"), "(1)")


class TestTyping(unittest.TestCase):
    def test_calculation_with_equals(self):
        calc = press_keys("1", "2", "+", "7", "=")
        self.assertEqual(calc.display, "19")

    def test_live_preview_while_typing(self):
        calc = press_keys("2", "×", "(", "3", "+", "4")
        self.assertEqual(calc.display, "2×(3+4")
        self.assertEqual(calc.preview, "= 14")

    def test_no_preview_for_a_plain_number(self):
        self.assertEqual(press_keys("4", "2").preview, "")

    def test_missing_brackets_are_closed_on_equals(self):
        self.assertEqual(press_keys("2", "×", "(", "3", "+", "4", "=").display, "14")

    def test_operator_replaces_previous_operator(self):
        self.assertEqual(press_keys("5", "+", "×").display, "5×")

    def test_no_leading_zeros(self):
        self.assertEqual(press_keys("0", "0", "7").display, "7")

    def test_only_one_decimal_point_per_number(self):
        self.assertEqual(press_keys("1", ".", ".", "5", ".").display, "1.5")

    def test_decimal_point_alone_becomes_zero_point(self):
        self.assertEqual(press_keys("+", ".").display, "0+0.")

    def test_negative_start(self):
        self.assertEqual(press_keys("−", "5", "×", "2", "=").display, "−10")

    def test_implicit_multiplication_with_brackets(self):
        self.assertEqual(press_keys("5", "(", "2", "=").display, "10")
        self.assertEqual(press_keys("(", "2", ")", "3", "=").display, "6")

    def test_close_bracket_needs_an_open_one(self):
        self.assertEqual(press_keys("5", ")").display, "5")

    def test_typing_after_result_starts_new_calculation(self):
        self.assertEqual(press_keys("2", "+", "2", "=", "5").display, "5")

    def test_operator_after_result_continues(self):
        self.assertEqual(press_keys("2", "+", "2", "=", "×", "3", "=").display, "12")

    def test_backspace_and_clear(self):
        self.assertEqual(press_keys("1", "2", "3", "⌫").display, "12")
        self.assertEqual(press_keys("1", "2", "+", "C").display, "0")

    def test_unknown_keys_are_ignored(self):
        self.assertEqual(press_keys("5", "", "a", "12").display, "5")


class TestFunctions(unittest.TestCase):
    def test_toggle_sign(self):
        self.assertEqual(press_keys("5", "±").display, "−5")
        self.assertEqual(press_keys("5", "±", "±").display, "5")
        self.assertEqual(press_keys("8", "×", "5", "±", "=").display, "−40")

    def test_percent(self):
        self.assertEqual(press_keys("5", "0", "%").display, "0.5")
        self.assertEqual(press_keys("2", "0", "0", "×", "1", "5", "%", "=").display, "30")

    def test_square_root(self):
        self.assertEqual(press_keys("1", "6", "√").display, "4")
        self.assertEqual(press_keys("2", "√").display, "1.41421356237")

    def test_square(self):
        self.assertEqual(press_keys("1", "2", "x²").display, "144")

    def test_function_applies_to_whole_expression(self):
        self.assertEqual(press_keys("9", "+", "7", "√").display, "4")


class TestErrors(unittest.TestCase):
    def test_divide_by_zero_message(self):
        calc = press_keys("5", "÷", "0", "=")
        self.assertEqual(calc.display, "Cannot divide by zero")
        self.assertTrue(calc.error)

    def test_incomplete_expression(self):
        self.assertEqual(press_keys("5", "+", "=").display, "Invalid expression")

    def test_square_root_of_negative(self):
        calc = press_keys("−", "4", "√")
        self.assertIn("negative", calc.display)

    def test_number_too_large(self):
        keys = ["9"] * 15 + ["x²"] * 3
        self.assertEqual(press_keys(*keys).display, "Number too large")

    def test_next_key_clears_the_error(self):
        self.assertEqual(press_keys("5", "÷", "0", "=", "7").display, "7")
        self.assertEqual(press_keys("5", "÷", "0", "=", "C").display, "0")

    def test_input_length_is_limited(self):
        calc = press_keys(*(["1"] * 100))
        self.assertLessEqual(len(calc.display), 60)


class TestHistory(unittest.TestCase):
    def test_calculations_are_saved(self):
        calc = press_keys("1", "+", "1", "=", "3", "×", "3", "=")
        self.assertEqual(calc.history, [("1+1", "2"), ("3×3", "9")])

    def test_functions_are_saved(self):
        self.assertEqual(press_keys("1", "6", "√").history, [("√(16)", "4")])

    def test_errors_are_not_saved(self):
        self.assertEqual(press_keys("5", "÷", "0", "=").history, [])

    def test_reuse_history_entry(self):
        calc = press_keys("1", "+", "1", "=", "3", "×", "3", "=")
        calc.use_history(0)
        self.assertEqual(calc.display, "2")
        self.assertEqual(calc.last_calculation, "1+1")
        calc.press("+")
        calc.press("5")
        calc.press("=")
        self.assertEqual(calc.display, "7")

    def test_clear_history(self):
        calc = press_keys("1", "+", "1", "=")
        calc.clear_history()
        self.assertEqual(calc.history, [])

    def test_history_has_a_limit(self):
        calc = Calculator()
        for _ in range(60):
            for key in ("1", "+", "1", "="):
                calc.press(key)
        self.assertEqual(len(calc.history), 50)


if __name__ == "__main__":
    unittest.main()