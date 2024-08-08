import io
import pytest  # noqa
from tempfile import NamedTemporaryFile
from typing import (
    cast,
)

from markdown_run import extract_code


CODE = """\
import sys


def func(x):
    print(sys.executable + " " + x)
"""


def check_extract_code(
    content_note: str,
    num_line: int,
    code_expected: str = CODE
) -> None:
    with NamedTemporaryFile(mode="w+") as file:
        print(content_note, file=file)
        file.flush()
        file.seek(0, 0)

        assert code_expected == extract_code(file.name, num_line)


@pytest.mark.parametrize("lang", ["python", ""])
def test_only_python_code(lang):
    check_extract_code(
        f"""\
```{lang}
{CODE}
```
""",
        2
    )
