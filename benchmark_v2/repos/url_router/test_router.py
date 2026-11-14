import pytest

from router import Router


def show_post(id, slug):
    return ("post", id, slug)


def search(q):
    return ("search", q)


def get_file(path):
    return ("file", path)


def list_items():
    return "items"


def create_item():
    return "created"


def feed():
    return "feed"


def make_router():
    r = Router()
    r.add("/users/<int:id>/posts/<slug:slug>", show_post, name="post")
    r.add("/search/<q>", search)
    r.add("/files/<path:path>", get_file, name="file")
    r.add("/items", list_items, methods=["GET"])
    r.add("/items", create_item, methods=["post", "put"])
    r.add("/feed.json", feed)
    return r


def test_match_converts_int():
    handler, params = make_router().match("GET", "/users/42/posts/hello-world")
    assert handler is show_post
    assert params == {"id": 42, "slug": "hello-world"}


def test_int_param_rejects_letters():
    assert make_router().dispatch("GET", "/users/abc/posts/x")[0] == 404


def test_path_param_spans_segments():
    assert make_router().dispatch("GET", "/files/docs/2023/report.pdf") == (200, ("file", "docs/2023/report.pdf"))


def test_dispatch_unquotes_str_param():
    assert make_router().dispatch("GET", "/search/caf%C3%A9") == (200, ("search", "café"))


def test_methods_are_case_insensitive():
    assert make_router().dispatch("POST", "/items") == (200, "created")


def test_head_falls_back_to_get():
    assert make_router().dispatch("HEAD", "/items") == (200, "items")


def test_405_lists_all_allowed_methods():
    assert make_router().dispatch("DELETE", "/items") == (405, "method not allowed; allowed: GET, POST, PUT")


def test_unknown_path_is_404():
    assert make_router().dispatch("GET", "/nope") == (404, "not found: /nope")


def test_first_route_wins():
    r = Router()
    r.add("/users/new", list_items)
    r.add("/users/<q>", search)
    assert r.dispatch("GET", "/users/new") == (200, "items")


def test_dot_in_pattern_is_literal():
    r = make_router()
    assert r.dispatch("GET", "/feed.json") == (200, "feed")
    assert r.dispatch("GET", "/feed-json")[0] == 404


def test_url_for_int_and_slug():
    assert make_router().url_for("post", id=7, slug="my-post") == "/users/7/posts/my-post"


def test_url_for_quotes_str():
    assert make_router().url_for("search", q="a/b c") == "/search/a%2Fb%20c"


def test_url_for_path_keeps_slashes():
    assert make_router().url_for("file", path="docs/a b.txt") == "/files/docs/a%20b.txt"


def test_url_for_missing_param():
    with pytest.raises(ValueError):
        make_router().url_for("post", id=7)


def test_url_for_rejects_bad_slug():
    with pytest.raises(ValueError):
        make_router().url_for("post", id=7, slug="Not A Slug")


def test_unknown_converter_rejected():
    with pytest.raises(ValueError):
        Router().add("/x/<float:v>", feed)
