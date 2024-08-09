from dataclasses import dataclass
import itertools as it
import pytest  # noqa
from tempfile import NamedTemporaryFile
from typing import (
    Sequence,
)

from markdown_run import extract_code, NoCodeThere


@dataclass
class Snippet:
    code: str

    def __str__(self) -> str:
        return self.code

    @property
    def lines(self) -> Sequence[str]:
        return str(self).split("\n")

    @property
    def num_lines(self) -> int:
        return len(self.lines)


CODE = Snippet("""\
import sys


def func(x):
    print(sys.executable + " " + x)
""")
ALT = Snippet("""\
from pathlib import Path
print(Path("note.md").read_text())
""")


def check_extract_code(
    content_note: str,
    num_line: int,
    code_expected: str = str(CODE)
) -> None:
    with NamedTemporaryFile(mode="w+") as file:
        file.write(content_note)
        file.flush()
        file.seek(0, 0)

        assert code_expected == extract_code(file.name, num_line)


@pytest.mark.parametrize(
    "lang,num_line",
    [
        ("python", 2),
        ("", 2),
        ("", 1),
    ] + [("python", i) for i in range(3, 8)]
)
def test_only_python_code(lang, num_line):
    check_extract_code(
        f"""\
```{lang}
{CODE}\
```
""",
        num_line
    )


def test_no_code_empty():
    with pytest.raises(NoCodeThere):
        check_extract_code("", 1)


@pytest.mark.parametrize("num_line", [9, 10, 1000])
def test_no_code_beyond_end(num_line):
    with pytest.raises(NoCodeThere):
        check_extract_code(
            f"""\
```
{CODE}\
```
""",
            num_line
        )


@pytest.mark.parametrize(
    "above,below,offset",
    it.starmap(
        lambda ab, n: (*ab, n),
        it.product(
            [
                ("asdf", "qwerty"),
                ("asdf\n", "\nqewrty"),
                ("asdf", ""),
                ("", "asdf"),
                (
                    """\
asdf

- qwerty
- zxcv

""",
                    """\

> asdf
>> qwerty
> zxcv
"""
                )
            ],
            range(CODE.num_lines)
        )
    )
)
def test_one_code_framed_by_content(above, below, offset):
    check_extract_code(
        f"""\
{above}
```python
{CODE}\
```
{below}
""",
        1 + len(above.split("\n")) + offset
    )


@pytest.mark.parametrize("line", [1, 2, 11, 13])
def test_one_code_line_outside_it(line):
    with pytest.raises(NoCodeThere):
        check_extract_code(
            f"""\
Some text above

```python
{CODE}\
```

More text below.

> One could even land in this quote!

""",
            line
        )


NOTE_TWO_CODES = f"""\
# Heading

Some text.

```python
{CODE}\
```

An explanation
of some sort.

> And then a quote.

```python
{ALT}\
```

Final thoughts:

1. This
2. Not that
"""


@pytest.mark.parametrize(
    "line,code_expected",
    it.chain(
        it.product([5, 6, 7, 8, 9, 10, 11, 12], [str(CODE)]),
        it.product([18, 19, 20, 21], [str(ALT)])
    )
)
def test_multiple_codes(line, code_expected):
    check_extract_code(
        NOTE_TWO_CODES,
        line,
        code_expected
    )


@pytest.mark.parametrize("line", [1, 2, 3, 4, 13, 14, 15, 16, 17, 23, 24, 25, 26])
def test_multiple_codes_outside(line):
    with pytest.raises(NoCodeThere):
        check_extract_code(NOTE_TWO_CODES, line)
