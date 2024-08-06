import obsessian as ob
import pytest  # noqa


def test_hello():
    assert ob.hello_world().startswith("Hello world")
