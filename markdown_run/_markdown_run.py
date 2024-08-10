from collections.abc import Sequence
from dataclasses import dataclass
import itertools as it
from mistletoe import Document, HTMLRenderer  # type: ignore
from mistletoe.block_token import CodeFence  # type: ignore
import os
from pathlib import Path
import re
from typing import (
    assert_never,
    cast,
    Never,
    Self,
    Union,
)


@dataclass
class Output:
    line: int
    span: int

    @classmethod
    def for_code_fence(cls, snippet: CodeFence, lines_note: Sequence[str]) -> Self:
        # Output should be inserted right after the bottom fence of the code.
        i_fence_top = snippet.line_number - 1
        assert re.match(r"^```", lines_note[i_fence_top])
        i_fence_bottom = i_fence_top + 1 + len(snippet.content.rstrip().split("\n"))
        assert re.match(r"^```\s*$", lines_note[i_fence_bottom])
        i_output = i_fence_bottom + 1
        try:
            if re.match(r"\^[-a-zA-Z0-9_]+\s*$", lines_note[i_output]):
                # This is an Obsidian block label.
                i_output += 1
        except IndexError:
            # We are already at the end of the file.
            pass
        return cls(line=i_output + 1, span=0)


@dataclass
class Executon:
    code: str
    output: Output

    @classmethod
    def make(cls, code: str, line_output: int, span_output: int) -> Self:
        return cls(code=code, output=Output(line=line_output, span=span_output))

    @classmethod
    def extract_from_note(cls, path_: Union[os.PathLike[str], str], line: int) -> Self:
        assert line >= 0
        note = _Note.parse(Path(path_)).check(line)
        snippet = note.find_snippet(line)
        return cls(
            code=snippet.content.rstrip() + "\n",
            output=Output.for_code_fence(snippet, note.lines)
        )


@dataclass
class _Note:
    path: Path
    lines: Sequence[str]
    doc: Document

    @classmethod
    def parse(cls, path: Path) -> "_Note":
        lines_note = path.read_text().split("\n")
        with HTMLRenderer():
            return cls(path=path, lines=lines_note, doc=Document(lines_note))

    def check(self, line: int) -> Self:
        if not self.doc.children:
            raise NoCodeThere(self.path, line)
        if line > self.line_last:
            raise NoCodeThere(self.path, line)
        return self

    @property
    def line_last(self) -> int:
        return len(self.lines)

    def find_snippet(self, line: int) -> CodeFence:
        for i, (line_start, line_end) in enumerate(
            it.pairwise(
                [ch.line_number for ch in self.doc.children] + [self.line_last + 1]
            )
        ):
            if line >= line_start and line < line_end:
                snippet = self.doc.children[i]
                break
        else:
            assert_never(cast(Never, i))  # noqa

        if not isinstance(snippet, CodeFence):
            raise NoCodeThere(self.path, line)
        assert snippet.language in {"", "python"}
        return snippet


@dataclass
class NoCodeThere(Exception):
    path: Path
    line: int
