"""In-memory todo store that can be saved to and loaded from a JSON string."""
import json
from dataclasses import asdict, dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    priority: int = 2  # 1 = high, 2 = normal, 3 = low


class TodoNotFound(KeyError):
    """Raised when no todo has the given id."""


class TodoStore:
    def __init__(self):
        self.todos = []
        self.next_id = 1

    def add(self, title: str, priority: int = 2) -> Todo:
        """Add a todo. Titles are stripped and must not be blank."""
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        if priority not in (1, 2, 3):
            raise ValueError("priority must be 1, 2 or 3")
        todo = Todo(self.next_id, title, priority=priority)
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo:
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        raise TodoNotFound(todo_id)

    def mark_done(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        todo.done = True
        return todo

    def remove(self, todo_id: int) -> Todo:
        todo = self.get(todo_id)
        self.todos.remove(todo)
        return todo

    def pending(self) -> list:
        """Todos not yet done, highest priority (1) first, then oldest first."""
        return sorted((t for t in self.todos if not t.done), key=lambda t: (t.priority, t.id))

    def to_json(self) -> str:
        return json.dumps({"next_id": self.next_id, "todos": [asdict(t) for t in self.todos]})

    @classmethod
    def from_json(cls, text: str) -> "TodoStore":
        """Load a store saved by to_json. Ids are never reused, even after removals."""
        store = cls()
        if not text.strip():
            return store
        data = json.loads(text)
        store.todos = [Todo(**item) for item in data["todos"]]
        store.next_id = data["next_id"]
        return store
