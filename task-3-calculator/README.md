# Task 3 – Calculator with GUI

A desktop calculator with a graphical interface built using **Tkinter**, Python's built-in GUI library. Built as part of the **Auspify Technologies Python Development Internship**.

## Features
- **Basic arithmetic**: addition, subtraction, multiplication and division, with the correct order of operations and brackets
- **Live results**: the answer updates as you type (e.g. `2×(3+4` shows `= 14`)
- **Extra functions**: square root (√), square (x²), percent (%) and sign change (±)
- **Calculation history**: a side panel lists past calculations. Click one to reuse its result
- **Keyboard support**: type calculations directly instead of clicking
- **Error handling**: clear messages for division by zero, incomplete expressions, the square root of a negative number and numbers that are too large
- **Input guards**: blocks double operators, repeated decimal points and leading zeros, closes missing brackets automatically, and limits the input length
- **Safe evaluation**: expressions are calculated with Python's `ast` module and a whitelist of allowed operations, never `eval()`, so typed input can't run code
- **Modern dark theme** with hover effects

## Skills Practised
Tkinter GUI · Event handling · Python functions · Classes · Error handling · Unit testing · Separating logic from the interface

## How to Run
Requires Python 3.8+ with Tkinter, which is included in the standard Windows and macOS installers. No extra libraries are needed.

```bash
cd task-3-calculator
py calculator.py
```

### Keyboard Shortcuts
| Key | Action |
|---|---|
| `0`–`9`, `.` | Numbers |
| `+` `-` `*` `/` | Operators (`x` also multiplies) |
| `(` `)` | Brackets |
| `Enter` or `=` | Calculate |
| `Backspace` | Delete last character |
| `Esc` or `Delete` | Clear |
| `%` | Percent |
| `r` / `s` | Square root / square |

## Screenshots
| Calculator | Live result while typing |
|---|---|
| ![Calculator](screenshots/calculator.png) | ![Live result](screenshots/live-result.png) |

| History panel | Error handling |
|---|---|
| ![History](screenshots/history.png) | ![Error](screenshots/error.png) |

## How It Works
The project is split into two parts:

- **`calculator_logic.py`**: all the rules. A `Calculator` class tracks the current expression, results and history, and decides what each key press does. Expressions are parsed into a syntax tree with `ast.parse`, and only numbers and `+ − × ÷` are allowed to be evaluated. Anything else, like function calls or names, is rejected.
- **`calculator.py`**: only the window. It draws the display, buttons and history panel, sends every button click or key press to the `Calculator`, and redraws the screen from its state.

Keeping the logic separate from the interface means it can be tested without opening a window.

### Function behaviour
- **%** divides the last number by 100. For example, `200×15%` gives `200×0.15 = 30`.
- **√** and **x²** apply to the value of the whole current expression.
- **±** switches the last number between positive and negative.

## Testing
The logic is covered by **45 unit tests** using Python's built-in `unittest` module: arithmetic, order of operations, formatting, typing rules, functions, error messages, history, and a check that code such as `__import__('os')` can't be run.

```bash
py -m unittest -v
```

## Project Structure
```
task-3-calculator/
├── calculator.py          # Tkinter interface (run this)
├── calculator_logic.py    # Calculation rules, evaluation and history
├── test_calculator.py     # Unit tests
├── README.md
└── screenshots/
```

## Author
**Aliyer Bakers Musaazi** – [GitHub](https://github.com/amusaazi-sudo) · [LinkedIn](https://linkedin.com/in/aliyer-musaazi)