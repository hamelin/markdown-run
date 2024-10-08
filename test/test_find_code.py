from dataclasses import dataclass
import itertools as it
import pytest  # noqa
from tempfile import NamedTemporaryFile
from typing import (
    Sequence,
)

from markdown_run import Executon, NoCodeThere


@dataclass
class SnippetFixture:
    code: str

    def __str__(self) -> str:
        return self.code

    @property
    def lines(self) -> Sequence[str]:
        return str(self).split("\n")

    @property
    def num_lines(self) -> int:
        return len(self.lines)


NEWLINE = "\n"
CODE = SnippetFixture("""\
import sys


def func(x):
    print(sys.executable + " " + x)
""")
ALT = SnippetFixture("""\
from pathlib import Path
print(Path("note.md").read_text())
""")


def check_extract_code(
    content_note: str,
    line: int,
    code_expected: str,
    output_line_expected: int,
    output_span_expected: int
) -> None:
    with NamedTemporaryFile(mode="w+") as file:
        file.write(content_note)
        file.flush()
        file.seek(0, 0)

        actual = Executon.extract_from_note(file.name, line)
        assert Executon.make(
            code_expected,
            output_line_expected,
            output_span_expected
        ) == actual


@pytest.mark.parametrize(
    "lang,line",
    [
        ("python", 2),
        ("", 2),
        ("", 1),
    ] + [("python", i) for i in range(3, 8)]
)
def test_only_python_code(lang, line):
    check_extract_code(
        f"""\
```{lang}
{CODE}\
```
""",
        line,
        str(CODE),
        8,
        0,
    )


def check_no_code_there(content_note: str, line: int) -> None:
    with pytest.raises(NoCodeThere):
        check_extract_code("", line, "dummy", 0, 0)


def test_no_code_empty():
    check_no_code_there("", 1)


@pytest.mark.parametrize("line", [9, 10, 1000])
def test_no_code_beyond_end(line):
    check_no_code_there(
        f"""\
```
{CODE}\
```
""",
        line,
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
    line_start_code = 1 + len(above.split("\n"))
    check_extract_code(
        f"""\
{above}
```python
{CODE}\
```
{below}
""",
        line_start_code + offset,
        str(CODE),
        line_start_code + CODE.num_lines + 1,
        0
    )


@pytest.mark.parametrize("line", [1, 2, 11, 13])
def test_one_code_line_outside_it(line):
    check_no_code_there(
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
    "line,code_expected,line_expected",
    it.chain(
        it.product([5, 6, 7, 8, 9, 10, 11, 12], [str(CODE)], [12]),
        it.product([18, 19, 20, 21], [str(ALT)], [22])
    )
)
def test_multiple_codes(line, code_expected, line_expected):
    check_extract_code(
        NOTE_TWO_CODES,
        line,
        code_expected,
        line_expected,
        0
    )


@pytest.mark.parametrize("line", [1, 2, 3, 4, 13, 14, 15, 16, 17, 23, 24, 25, 26])
def test_multiple_codes_outside(line):
    check_no_code_there(NOTE_TWO_CODES, line)


@pytest.mark.parametrize(
    "sep,line,code_expected,line_expected",
    [
        (2, 9, str(CODE), 10),
        (2, 11, str(CODE), 10),
        (2, 12, str(ALT), 16),
        (1, 9, str(CODE), 10),
        (1, 10, str(CODE), 10),
        (1, 11, str(ALT), 15),
        (0, 9, str(CODE), 10),
        (0, 10, str(ALT), 14),
    ]
)
def test_codes_juxtaposed(sep, line, code_expected, line_expected):
    check_extract_code(
        f"""\
Some stuff before.

```
{CODE}\
```
{NEWLINE * sep}\
```
{ALT}\
```

Stuff after.
""",
        line,
        code_expected,
        line_expected,
        0
    )


def test_indented_preformatting_not_code():
    check_no_code_there(
        """
The following block will not be understood as runnable code:

    import sys
    print(sys.path)

It is what it is.
""",
        3
    )


def test_code_tagged_with_obsidian_block_label():
    check_extract_code(
        f"""\
```python
{CODE}\
```
^the_code

Coda.
""",
        2,
        str(CODE),
        9,
        0,
    )


@pytest.mark.parametrize("coda", ["", "\n^thedef"])
def test_code_output_extends_file(coda):
    check_extract_code(
        f"""\
```
{CODE}\
```{coda}""",
        2,
        str(CODE),
        7 + len(coda.split("\n")),
        0
    )


@pytest.mark.parametrize("label", ["", "^a_label"])
def test_code_output_follows(label):
    check_extract_code(
        f"""\
# Heading

```python
{ALT}\
```
{label}
<div class="markdown-run-output">
<pre>
asdf
qwerty
</pre>
</div>

Bottom matter.
""",
        4,
        str(ALT),
        8,
        6
    )


def test_code_output_further_below():
    check_extract_code(
        f"""\
# Heading

```python
{ALT}\
```

Then a paragraph of text.

1. And also a list.
1. With two items.

<div class="markdown-run-output">
<pre>
asdf
qwerty
</pre>
</div>
""",
        5,
        str(ALT),
        13,
        6,
    )


def test_code_output_no_proper_class():
    check_extract_code(
        f"""\
# Heading

```python
{ALT}\
```



<div>
<pre>
asdf
qwerty
</pre>
</div>
""",
        5,
        str(ALT),
        7,
        0,
    )
    pytest.fail()
