import pytest

from registry import Registry
from validation import ValidationError

PASSWORD = "s3cret-pass"


def test_register_and_authenticate():
    reg = Registry()
    reg.register("alice", PASSWORD)
    assert reg.authenticate("alice", PASSWORD)


def test_wrong_password_fails():
    reg = Registry()
    reg.register("alice", PASSWORD)
    assert not reg.authenticate("alice", "wrong-pass1")


def test_duplicate_username_is_case_insensitive():
    reg = Registry()
    reg.register("Alice", PASSWORD)
    with pytest.raises(ValidationError):
        reg.register("alice", PASSWORD)


def test_lookup_ignores_case_and_spaces():
    reg = Registry()
    reg.register("  Carol ", PASSWORD)
    assert reg.get("CAROL").username == "Carol"


def test_unknown_role_rejected_and_not_stored():
    reg = Registry()
    with pytest.raises(ValidationError):
        reg.register("dave", PASSWORD, roles=("superuser",))
    with pytest.raises(KeyError):
        reg.get("dave")


def test_admin_inherits_all_permissions():
    reg = Registry()
    reg.register("ann", PASSWORD, roles=("admin",))
    assert all(reg.can("ann", p) for p in ("read", "comment", "write", "delete"))


def test_deactivated_user_loses_access():
    reg = Registry()
    reg.register("erin", PASSWORD, roles=("editor",))
    reg.deactivate("erin")
    assert not reg.authenticate("erin", PASSWORD)
    assert not reg.can("erin", "write")


def test_reactivated_user_regains_access():
    reg = Registry()
    reg.register("erin", PASSWORD, roles=("editor",))
    reg.deactivate("erin")
    reg.activate("erin")
    assert reg.can("erin", "write")


def test_grant_role_adds_permissions():
    reg = Registry()
    reg.register("dana", PASSWORD)
    assert not reg.can("dana", "write")
    reg.grant("dana", "editor")
    assert reg.can("dana", "write")
