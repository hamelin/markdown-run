from contextlib import contextmanager
import pytest  # noqa
from tempfile import NamedTemporaryFile
from typing import Iterator

from markdown_run import extract_code


@contextmanager
def note_temp(content: str) -> Iterator:
    with NamedTemporaryFile(mode="w+") as file:
        print(content, file=file)
        file.flush()
        file.seek(0, 0)
        yield file


def test_only_python_code():
    code = """\
def hey():
    return 0
""".lstrip()
    with note_temp(
        f"""\
```python
{code}
```
"""
    ) as file:
        assert extract_code(file, 2) == code


def test_only_unlabeled_code():
    code = """\
def hey():
    return 0
"""
    with note_temp(
        f"""\
```
{code}
```
"""
    ) as file:
        assert extract_code(file, 2) == code
