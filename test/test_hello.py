import pytest  # noqa

from markdown_run import hello_world


def test_hello():
    assert hello_world().startswith("Hello world")
