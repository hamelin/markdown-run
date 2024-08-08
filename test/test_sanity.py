from pathlib import Path
import pytest  # noqa

import markdown_run


def test_is_dev_module():
    assert markdown_run.__file__ == str(Path("markdown_run/__init__.py").resolve())
