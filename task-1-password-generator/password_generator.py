"""
Password Generator
Auspify Technologies - Python Development Internship (Task 1)
Author: Aliyer Bakers Musaazi

Generates secure, customizable passwords from letters, numbers and symbols.
Uses random.SystemRandom, which draws from the operating system's secure
random source, so passwords are safe to use for real accounts.
"""

import random
import string

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

console = Console()
rng = random.SystemRandom()  # cryptographically secure random generator

MIN_LENGTH = 4
MAX_LENGTH = 128
MAX_COUNT = 20

CHARACTER_SETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "numbers": string.digits,
    "symbols": "!@#$%^&*()-_=+[]{};:,.?/",
}


# ---------- Core logic ----------

def generate_password(length, selected_sets):
    """
    Build a random password of the given length.
    Guarantees at least one character from every selected set,
    then fills the rest from all selected characters and shuffles.
    """
    if not selected_sets:
        raise ValueError("Select at least one character type.")
    if length < len(selected_sets):
        raise ValueError(f"Length must be at least {len(selected_sets)} for the selected options.")

    pool = "".join(selected_sets)
    password = [rng.choice(chars) for chars in selected_sets]
    password += [rng.choice(pool) for _ in range(length - len(password))]
    rng.shuffle(password)
    return "".join(password)


def password_strength(password):
    """Rate a password as Weak, Medium, Strong or Very Strong."""
    variety = sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in CHARACTER_SETS["symbols"] for c in password),
    ])
    length = len(password)

    if length >= 16 and variety >= 3:
        return "Very Strong", "bold green"
    if length >= 12 and variety >= 3:
        return "Strong", "green"
    if length >= 8 and variety >= 2:
        return "Medium", "yellow"
    return "Weak", "red"


# ---------- User input ----------

def ask_length():
    while True:
        length = IntPrompt.ask(f"[cyan]Password length[/] ({MIN_LENGTH}-{MAX_LENGTH})", default=16)
        if MIN_LENGTH <= length <= MAX_LENGTH:
            return length
        console.print(f"[red]✘ Length must be between {MIN_LENGTH} and {MAX_LENGTH}.[/]")


def ask_character_sets():
    while True:
        selected = []
        for name, chars in CHARACTER_SETS.items():
            if Confirm.ask(f"Include [bold]{name}[/] ({escape(chars[:10])}...)?", default=True):
                selected.append(chars)
        if selected:
            return selected
        console.print("[red]✘ Please choose at least one character type.[/]")


def ask_count():
    while True:
        count = IntPrompt.ask(f"[cyan]How many passwords?[/] (1-{MAX_COUNT})", default=1)
        if 1 <= count <= MAX_COUNT:
            return count
        console.print(f"[red]✘ Choose a number between 1 and {MAX_COUNT}.[/]")


# ---------- Display ----------

def show_passwords(passwords):
    table = Table(title="🔐 Generated Passwords", header_style="bold magenta")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Password", style="bold white")
    table.add_column("Length", justify="center")
    table.add_column("Strength", justify="center")

    for i, pwd in enumerate(passwords, start=1):
        label, style = password_strength(pwd)
        table.add_row(str(i), escape(pwd), str(len(pwd)), f"[{style}]{label}[/]")

    console.print(table)


# ---------- Main ----------

def main():
    console.print(Panel.fit(
        "[bold white]Password Generator[/]\n[dim]Auspify Python Internship · Task 1[/]",
        border_style="bright_blue",
    ))

    while True:
        console.print()
        length = ask_length()
        selected_sets = ask_character_sets()

        if length < len(selected_sets):
            console.print(f"[red]✘ Length must be at least {len(selected_sets)} "
                          f"to include every selected type.[/]")
            continue

        count = ask_count()
        passwords = [generate_password(length, selected_sets) for _ in range(count)]
        show_passwords(passwords)

        if not Confirm.ask("\nGenerate more passwords?", default=True):
            console.print("[bold blue]Stay secure! 👋[/]")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold blue]Stay secure! 👋[/]")