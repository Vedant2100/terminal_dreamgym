"""In-memory user registry with roles and deactivation."""
import hashlib
from dataclasses import dataclass, field

from roles import ROLES, has_permission
from validation import ValidationError, check_password, check_username, normalize_username


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + password).encode()).hexdigest()


@dataclass
class User:
    username: str  # display name, as typed at registration (without surrounding spaces)
    password_hash: str
    roles: set = field(default_factory=set)
    active: bool = True


class Registry:
    def __init__(self, salt: str = "registry"):
        self.salt = salt
        self._users = {}  # normalised username -> User

    def register(self, username: str, password: str, roles=("viewer",)) -> User:
        """Create a user. Nothing is stored if any rule is broken."""
        key = check_username(username)
        if key in self._users:
            raise ValidationError(f"username {username!r} is taken")
        check_password(password, username)
        for role in roles:
            if role not in ROLES:
                raise ValidationError(f"unknown role: {role}")
        user = User(username.strip(), hash_password(password, self.salt), set(roles))
        self._users[key] = user
        return user

    def get(self, username: str) -> User:
        return self._users[normalize_username(username)]

    def authenticate(self, username: str, password: str) -> bool:
        """True if the user exists, is active and the password matches."""
        user = self._users.get(normalize_username(username))
        if user is None or not user.active:
            return False
        return user.password_hash == hash_password(password, self.salt)

    def grant(self, username: str, role: str) -> None:
        if role not in ROLES:
            raise ValidationError(f"unknown role: {role}")
        self.get(username).roles.add(role)

    def deactivate(self, username: str) -> None:
        """Deactivated users keep their roles but cannot log in or act."""
        self.get(username).active = False

    def activate(self, username: str) -> None:
        self.get(username).active = True

    def can(self, username: str, permission: str) -> bool:
        """Whether an active user holds `permission` through any of their roles."""
        user = self.get(username)
        if not user.active:
            return False
        return any(has_permission(role, permission) for role in user.roles)
