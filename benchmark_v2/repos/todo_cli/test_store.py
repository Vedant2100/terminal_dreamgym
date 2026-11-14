import pytest

from store import TodoStore


def test_add_rejects_bad_priority():
    with pytest.raises(ValueError):
        TodoStore().add("x", priority=0)


def test_roundtrip_json():
    store = TodoStore()
    store.add("a")
    store.add("b", priority=1)
    store.mark_done(1)
    restored = TodoStore.from_json(store.to_json())
    assert restored.todos == store.todos


def test_ids_not_reused_after_reload():
    store = TodoStore()
    for title in ("a", "b", "c"):
        store.add(title)
    store.remove(2)
    restored = TodoStore.from_json(store.to_json())
    assert restored.add("d").id == 4


def test_from_blank_text_is_empty():
    store = TodoStore.from_json("  ")
    assert store.todos == []
    assert store.add("a").id == 1
