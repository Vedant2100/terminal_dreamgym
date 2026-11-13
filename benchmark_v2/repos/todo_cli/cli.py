"""Command-line interface: todo add | list | done | remove."""
import argparse
import sys

from render import format_list, format_todo
from store import TodoNotFound, TodoStore

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_INVALID = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="add a todo")
    add.add_argument("title", nargs="+")
    add.add_argument("-p", "--priority", type=int, default=2)
    show = sub.add_parser("list", help="list pending todos")
    show.add_argument("--all", action="store_true", help="include finished todos, in id order")
    for name in ("done", "remove"):
        cmd = sub.add_parser(name)
        cmd.add_argument("id", type=int)
    return parser


def main(argv=None, store=None) -> int:
    """Run one command against `store` and return the exit code.

    Normal output goes to stdout. Errors go to stderr as 'error: ...' with exit
    code 1 for an unknown id and 2 for invalid input.
    """
    store = store if store is not None else TodoStore()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "add":
            todo = store.add(" ".join(args.title), args.priority)
            print(f"added {todo.id}")
        elif args.command == "list":
            todos = store.todos if args.all else store.pending()
            print(format_list(todos))
        elif args.command == "done":
            todo = store.get(args.id)
            if todo.done:
                print(f"todo {todo.id} is already done")
            else:
                store.mark_done(args.id)
                print(format_todo(todo))
        elif args.command == "remove":
            todo = store.remove(args.id)
            print(f"removed {todo.id}: {todo.title}")
    except TodoNotFound as exc:
        print(f"error: no todo with id {exc.args[0]}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK
