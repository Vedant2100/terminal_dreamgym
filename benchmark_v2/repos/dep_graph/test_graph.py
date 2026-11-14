from graph import DepGraph

DIAMOND = "a -> c\nb -> c\nc -> d"


def test_undeclared_dependency_is_a_node():
    assert DepGraph.from_text("a -> b").deps == {"a": ["b"], "b": []}


def test_direct_dependents():
    g = DepGraph.from_text(DIAMOND)
    assert g.dependents("c") == ["a", "b"]
    assert g.dependents("d") == ["c"]


def test_transitive_dependents():
    g = DepGraph.from_text(DIAMOND)
    assert g.dependents("d", transitive=True) == ["a", "b", "c"]


def test_find_cycle_from_start():
    g = DepGraph.from_text("a -> b\nb -> c\nc -> a\nd")
    assert g.find_cycle() == ["a", "b", "c", "a"]


def test_find_cycle_not_through_first_node():
    g = DepGraph.from_text("a -> b\nb -> c\nc -> b")
    assert g.find_cycle() == ["b", "c", "b"]
