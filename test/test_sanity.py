import obsessian as ob
from pathlib import Path
import pytest  # noqa


def test_is_dev_module():
    assert ob.__file__ == str(Path("obsessian/__init__.py").resolve())
