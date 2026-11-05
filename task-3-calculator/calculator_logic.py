"""
Calculator logic, kept separate from the GUI so it can be tested on its own.

Expressions are evaluated with Python's `ast` module and a whitelist of
allowed operations, instead of eval(), so typed input can never run code.
"""

import ast
import math
import operator
import re

PLUS, MINUS, TIMES, DIVIDE = "+", "−", "×", "÷"
OPERATORS = (PLUS, MINUS, TIMES, DIVIDE)
DIGITS = "0123456789"
MAX_LENGTH = 60
MAX_HISTORY = 50
MAX_MAGNITUDE = 10**100

# Matches the number at the end of an expression, e.g. "12", "3.5", ".5", "1e+20"
LAST_NUMBER = re.compile(r"(\d+\.?\d*(?:e[+-]?\d+)?|\.\d+)$")

ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class CalculatorError(Exception):
    """Raised for any input the calculator cannot evaluate."""


# ---------- Evaluation ----------


def evaluate(expression):
    """Safely evaluate a calculator expression such as '12×(3−1)÷4'."""
    text = expression.replace(TIMES, "*").replace(DIVIDE, "/").replace(MINUS, "-")
    if not text.strip():
        raise CalculatorError("Nothing to calculate")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        raise CalculatorError("Invalid expression") from None

    try:
        value = _evaluate_node(tree.body)
    except ZeroDivisionError:
        raise CalculatorError("Cannot divide by zero") from None
    except OverflowError:
        raise CalculatorError("Number too large") from None

    return check_size(value)


def check_size(value):
    """Reject results that are infinite or too large to display sensibly."""
    if isinstance(value, float) and not math.isfinite(value):
        raise CalculatorError("Number too large")
    if abs(value) > MAX_MAGNITUDE:
        raise CalculatorError("Number too large")
    return value


def _evaluate_node(node):
    """Recursively evaluate only numbers and + − × ÷ operations."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        return ALLOWED_BINARY[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY:
        return ALLOWED_UNARY[type(node.op)](_evaluate_node(node.operand))
    raise CalculatorError("Invalid expression")


def format_number(value):
    """Format a result for display: no trailing '.0', at most 12 significant digits."""
    if value == 0:
        return "0"
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        value = int(value)
    if isinstance(value, int) and abs(value) < 10**15:
        text = str(value)
    else:
        text = f"{value:.12g}"
    # Use the display minus sign for negative numbers (but not inside "1e-05")
    return MINUS + text[1:] if text.startswith("-") else text


def balance_parentheses(expression):
    """Add any missing closing brackets, e.g. '2×(3+4' -> '2×(3+4)'."""
    missing = expression.count("(") - expression.count(")")
    return expression + ")" * max(missing, 0)


# ---------- Calculator state ----------


class Calculator:
    """Holds the current expression, the result state and the history."""

    def __init__(self):
        self.expression = ""
        self.error = None
        self.just_evaluated = False
        self.last_calculation = ""  # the expression the current result came from
        self.history = []  # list of (expression, result), oldest first

    # ----- What the GUI shows -----

    @property
    def display(self):
        if self.error:
            return self.error
        return self.expression or "0"

    @property
    def preview(self):
        """Live result shown while typing, e.g. '= 42'. Empty when not useful."""
        if self.error or self.just_evaluated or not self.expression:
            return ""
        if not any(symbol in self.expression for symbol in OPERATORS + ("(",)):
            return ""
        try:
            result = format_number(evaluate(balance_parentheses(self.expression)))
        except CalculatorError:
            return ""
        return "" if result == self.expression else f"= {result}"

    # ----- Input -----

    def press(self, key):
        """Handle one button press or key, e.g. '7', '+', '=', 'C', '√'."""
        if not key:
            return
        if self.error:
            self.error = None
            self.expression = ""
            self.just_evaluated = False
            if key in ("C", "⌫"):
                return

        if len(key) == 1 and key in DIGITS:
            self._add_digit(key)
        elif key == ".":
            self._add_decimal_point()
        elif key in OPERATORS:
            self._add_operator(key)
        elif key == "(":
            self._open_bracket()
        elif key == ")":
            self._close_bracket()
        elif key == "=":
            self.calculate()
        elif key == "C":
            self.clear()
        elif key == "⌫":
            self._backspace()
        elif key == "±":
            self._toggle_sign()
        elif key == "%":
            self._percent()
        elif key == "√":
            self._apply_function("√", self._square_root)
        elif key == "x²":
            self._apply_function("sqr", lambda x: x * x)

    def clear(self):
        self.expression = ""
        self.error = None
        self.just_evaluated = False

    def calculate(self):
        if not self.expression:
            return
        expression = balance_parentheses(self.expression)
        try:
            result = format_number(evaluate(expression))
        except CalculatorError as error:
            self._show_error(error)
            return
        self._add_history(expression, result)
        self.expression = result
        self.just_evaluated = True

    def use_history(self, index):
        """Load the result of a history entry so it can be used again."""
        if 0 <= index < len(self.history):
            self.error = None
            self.last_calculation, self.expression = self.history[index]
            self.just_evaluated = True

    def clear_history(self):
        self.history.clear()

    # ----- Helpers -----

    def _last_char(self):
        return self.expression[-1] if self.expression else ""

    def _append(self, text):
        if len(self.expression) + len(text) <= MAX_LENGTH:
            self.expression += text

    def _start_fresh_after_result(self):
        """After '=', typing a new number starts a new calculation."""
        if self.just_evaluated:
            self.expression = ""
            self.just_evaluated = False

    def _add_digit(self, digit):
        self._start_fresh_after_result()
        last_number = LAST_NUMBER.search(self.expression)
        if last_number and last_number.group() == "0":
            self.expression = self.expression[:-1]  # no leading zeros like "07"
        elif self._last_char() == ")":
            self._append(TIMES)
        self._append(digit)

    def _add_decimal_point(self):
        self._start_fresh_after_result()
        last_number = LAST_NUMBER.search(self.expression)
        if last_number:
            if "." not in last_number.group() and "e" not in last_number.group():
                self._append(".")
        elif self._last_char() == ")":
            self._append(TIMES + "0.")
        else:
            self._append("0.")

    def _add_operator(self, symbol):
        self.just_evaluated = False
        last = self._last_char()
        if not self.expression:
            self.expression = MINUS if symbol == MINUS else "0" + symbol
        elif last == "(":
            if symbol == MINUS:
                self._append(MINUS)
        elif last in OPERATORS:
            if len(self.expression) == 1 or self.expression[-2] == "(":
                return  # keep a leading minus such as "−" or "(−"
            self.expression = self.expression[:-1] + symbol
        else:
            self._append(symbol)

    def _open_bracket(self):
        self._start_fresh_after_result()
        last = self._last_char()
        if last and last in DIGITS + ".)":
            self._append(TIMES)
        self._append("(")

    def _close_bracket(self):
        self.just_evaluated = False
        last = self._last_char()
        open_brackets = self.expression.count("(") - self.expression.count(")")
        if open_brackets > 0 and last not in OPERATORS + ("(", ""):
            self._append(")")

    def _backspace(self):
        self.just_evaluated = False
        self.expression = self.expression[:-1]

    def _toggle_sign(self):
        """Make the last number negative or positive again."""
        self.just_evaluated = False
        match = LAST_NUMBER.search(self.expression)
        if not match:
            return
        start = match.start()
        before, number = self.expression[:start], match.group()
        if before.endswith("(" + MINUS):
            self.expression = before[:-2] + number
        elif before == MINUS:
            self.expression = number
        elif before == "":
            self.expression = MINUS + number
        else:
            self.expression = before + "(" + MINUS + number

    def _percent(self):
        """Divide the last number by 100, e.g. '200×15' -> '200×0.15'."""
        self.just_evaluated = False
        match = LAST_NUMBER.search(self.expression)
        if match:
            value = evaluate(match.group()) / 100
            self.expression = self.expression[: match.start()] + format_number(value)

    def _apply_function(self, name, function):
        """Apply √ or x² to the value of the whole current expression."""
        if not self.expression:
            return
        expression = balance_parentheses(self.expression)
        try:
            result = format_number(check_size(function(evaluate(expression))))
        except CalculatorError as error:
            self._show_error(error)
            return
        except OverflowError:
            self._show_error(CalculatorError("Number too large"))
            return
        self._add_history(f"{name}({expression})", result)
        self.expression = result
        self.just_evaluated = True

    @staticmethod
    def _square_root(value):
        if value < 0:
            raise CalculatorError("Invalid input: √ of a negative number")
        return math.sqrt(value)

    def _show_error(self, error):
        self.error = str(error)
        self.just_evaluated = False

    def _add_history(self, expression, result):
        self.last_calculation = expression
        self.history.append((expression, result))
        del self.history[:-MAX_HISTORY]