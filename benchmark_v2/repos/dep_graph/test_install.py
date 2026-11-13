import pytest

from graph import CycleError, DepGraph
from install import install_order


def test_ties_broken_alphabetically():
    g = DepGraph.from_text("zip\napp -> web, db\nweb -> lib\ndb -> lib")
    assert install_order(g) == ["lib", "db", "web", "app", "zip"]


def test_dependencies_come_first():
    g = DepGraph.from_text("a -> b\nb -> c")
    assert install_order(g) == ["c", "b", "a"]


def test_targets_limit_the_order():
    g = DepGraph.from_text("app -> lib\ncli -> term")
    assert install_order(g, ["app"]) == ["lib", "app"]


def test_cycle_raises_with_path():
    g = DepGraph.from_text("a -> b\nb -> c\nc -> a\nd")
    with pytest.raises(CycleError) as exc:
        install_order(g)
    assert exc.value.cycle == ["a", "b", "c", "a"]
    assert "a -> b -> c -> a" in str(exc.value)


def test_redeclared_package_keeps_all_dependencies():
    g = DepGraph.from_text("app -> lib\napp -> aux\nlib -> core")
    assert install_order(g, ["app"]) == ["aux", "core", "lib", "app"]


def test_repeated_dependency_counted_once():
    g = DepGraph.from_text("app -> lib\napp -> lib, util")
    assert install_order(g) == ["lib", "util", "app"]
