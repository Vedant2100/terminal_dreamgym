from cli import main
from store import TodoStore


def test_add_prints_new_id(capsys):
    store = TodoStore()
    assert main(["add", "buy", "milk"], store) == 0
    assert capsys.readouterr().out == "added 1\n"
    assert store.get(1).title == "buy milk"


def test_add_blank_title_is_invalid(capsys):
    assert main(["add", "  "], TodoStore()) == 2
    assert capsys.readouterr().err == "error: title must not be empty\n"


def test_list_empty(capsys):
    assert main(["list"], TodoStore()) == 0
    assert capsys.readouterr().out == "nothing to do\n"


def test_list_pending_by_priority(capsys):
    store = TodoStore()
    store.add("water plants", priority=3)
    store.add("pay rent", priority=1)
    store.add("call mum")
    main(["list"], store)
    assert capsys.readouterr().out == "[ ] 2 pay rent !!\n[ ] 3 call mum !\n[ ] 1 water plants\n"


def test_list_hides_done(capsys):
    store = TodoStore()
    store.add("a")
    store.add("b")
    store.mark_done(1)
    main(["list"], store)
    assert capsys.readouterr().out == "[ ] 2 b !\n"


def test_list_all_shows_done_marks(capsys):
    store = TodoStore()
    store.add("a")
    store.add("b")
    store.mark_done(1)
    main(["list", "--all"], store)
    assert capsys.readouterr().out == "[x] 1 a !\n[ ] 2 b !\n"


def test_done_prints_checked_line(capsys):
    store = TodoStore()
    store.add("pay rent", priority=1)
    assert main(["done", "1"], store) == 0
    assert capsys.readouterr().out == "[x] 1 pay rent !!\n"
    assert store.get(1).done


def test_done_twice_is_not_an_error(capsys):
    store = TodoStore()
    store.add("a")
    main(["done", "1"], store)
    capsys.readouterr()
    assert main(["done", "1"], store) == 0
    assert capsys.readouterr().out == "todo 1 is already done\n"


def test_done_unknown_id(capsys):
    assert main(["done", "7"], TodoStore()) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: no todo with id 7\n"


def test_remove_prints_title(capsys):
    store = TodoStore()
    store.add("a")
    store.add("b")
    assert main(["remove", "1"], store) == 0
    assert capsys.readouterr().out == "removed 1: a\n"
    assert [t.id for t in store.todos] == [2]


def test_remove_after_earlier_removal(capsys):
    store = TodoStore()
    for title in ("a", "b", "c"):
        store.add(title)
    main(["remove", "2"], store)
    capsys.readouterr()
    assert main(["remove", "3"], store) == 0
    assert capsys.readouterr().out == "removed 3: c\n"
    assert [t.id for t in store.todos] == [1]
