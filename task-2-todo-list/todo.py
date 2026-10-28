"""
To-Do List Application
Auspify Technologies - Python Development Internship (Task 2)
Author: Aliyer Bakers Musaazi

A command-line app to add, view, complete and delete tasks.
Tasks are saved to tasks.json so they persist between runs.
Uses the Rich library for a colourful, readable terminal interface.
"""

import json
import os
from datetime import date

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
console = Console()


# ---------- Storage ----------

def load_tasks():
    """Load tasks from the JSON file. Return an empty list if none exist."""
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        console.print("[yellow]Warning: could not read tasks file. Starting with an empty list.[/]")
        return []


def save_tasks(tasks):
    """Save the task list to the JSON file."""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


# ---------- Helpers ----------

def next_id(tasks):
    """Return the next available task id."""
    return max((t["id"] for t in tasks), default=0) + 1


def find_task(tasks, task_id):
    """Return the task with the given id, or None."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def success(message):
    console.print(f"[bold green]✔[/] {message}")


def error(message):
    console.print(f"[bold red]✘[/] {message}")


# ---------- Actions ----------

def add_task(tasks):
    title = Prompt.ask("[cyan]Enter task title[/]").strip()
    if not title:
        error("Task title cannot be empty.")
        return
    task = {
        "id": next_id(tasks),
        "title": title,
        "done": False,
        "created": date.today().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    success(f"Added task #{task['id']}: [bold]{escape(title)}[/]")


def view_tasks(tasks):
    if not tasks:
        console.print(Panel("No tasks yet. Add one to get started!", style="dim", expand=False))
        return

    done_count = sum(1 for t in tasks if t["done"])
    pending = len(tasks) - done_count

    table = Table(
        title="📋 Your Tasks",
        caption=f"[yellow]{pending} pending[/] · [green]{done_count} done[/]",
        header_style="bold magenta",
        show_lines=False,
    )
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Task", style="white")
    table.add_column("Added", style="dim", no_wrap=True)

    for t in tasks:
        if t["done"]:
            status = "[green]✅ Done[/]"
            title = f"[strike dim]{escape(t['title'])}[/]"
        else:
            status = "[yellow]⏳ Pending[/]"
            title = escape(t["title"])
        table.add_row(str(t["id"]), status, title, t["created"])

    console.print(table)


def ask_for_existing_task(tasks, action_word):
    """Show the tasks, ask for an id and return the matching task (or None)."""
    view_tasks(tasks)
    task_id = IntPrompt.ask(f"[cyan]Enter the id of the task to {action_word}[/]")
    task = find_task(tasks, task_id)
    if task is None:
        error(f"No task with id {task_id}.")
    return task


def complete_task(tasks):
    if not tasks:
        error("No tasks to complete.")
        return
    task = ask_for_existing_task(tasks, "mark as done")
    if task is None:
        return
    if task["done"]:
        console.print("[yellow]That task is already completed.[/]")
        return
    task["done"] = True
    save_tasks(tasks)
    success(f"Marked task #{task['id']} as done. Nice work! 🎉")


def delete_task(tasks):
    if not tasks:
        error("No tasks to delete.")
        return
    task = ask_for_existing_task(tasks, "delete")
    if task is None:
        return
    if Confirm.ask(f"[red]Delete[/] '[bold]{escape(task['title'])}[/]'?"):
        tasks.remove(task)
        save_tasks(tasks)
        success(f"Deleted task #{task['id']}.")
    else:
        console.print("[dim]Delete cancelled.[/]")


# ---------- Main menu ----------

MENU = (
    "[bold cyan]1[/] Add task\n"
    "[bold cyan]2[/] View tasks\n"
    "[bold cyan]3[/] Mark task as done\n"
    "[bold cyan]4[/] Delete task\n"
    "[bold cyan]5[/] Exit"
)


def main():
    tasks = load_tasks()
    actions = {
        "1": add_task,
        "2": view_tasks,
        "3": complete_task,
        "4": delete_task,
    }

    console.print(Panel.fit("[bold white]To-Do List App[/]\n[dim]Auspify Python Internship · Task 2[/]",
                            border_style="bright_blue"))
    while True:
        console.print()
        console.print(Panel(MENU, title="Menu", border_style="blue", expand=False))
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])

        if choice == "5":
            console.print("[bold blue]Goodbye! 👋[/]")
            break
        actions[choice](tasks)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold blue]Goodbye! 👋[/]")