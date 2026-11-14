"""Plain-text formatting of todos for the terminal."""

PRIORITY_MARKS = {1: "!!", 2: "!", 3: ""}


def format_todo(todo) -> str:
    """One line per todo, e.g. '[x] 3 pay rent !!' (box, id, title, priority marks)."""
    box = "[x]" if todo.done else "[ ]"
    line = f"{box} {todo.id} {todo.title}"
    marks = PRIORITY_MARKS[todo.priority]
    return f"{line} {marks}" if marks else line


def format_list(todos) -> str:
    if not todos:
        return "nothing to do"
    return "\n".join(format_todo(todo) for todo in todos)
