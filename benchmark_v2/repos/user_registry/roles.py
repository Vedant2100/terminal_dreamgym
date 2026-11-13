"""Roles and the permissions they grant. A role inherits everything its parent has."""

ROLES = {
    "viewer": {"parent": None, "grants": {"read"}},
    "editor": {"parent": "viewer", "grants": {"write", "comment"}},
    "admin": {"parent": "editor", "grants": {"delete", "manage_users"}},
}


def permissions_for(role: str) -> set:
    """All permissions of `role`, including inherited ones. Unknown roles raise KeyError."""
    perms = set()
    while role is not None:
        entry = ROLES[role]
        perms |= entry["grants"]
        role = entry["parent"]
    return perms


def has_permission(role: str, permission: str) -> bool:
    return permission in permissions_for(role)
