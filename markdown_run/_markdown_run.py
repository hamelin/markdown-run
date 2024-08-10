from dataclasses import dataclass
import itertools as it
from mistletoe import Document, HTMLRenderer  # type: ignore
from mistletoe.block_token import BlockCode, CodeFence  # type: ignore
import os
from pathlib import Path
from typing import (
    Tuple,
    Union,
)


def extract_code_and_output(
    path_: Union[os.PathLike[str], str],
    line: int
) -> Tuple[str, int]:
    assert line >= 0
    path = Path(path_)
    lines_note = path.read_text().split("\n")
    with HTMLRenderer():
        doc = Document(lines_note)
    if not doc.children:
        raise NoCodeThere(path, line)
    line_last = len(lines_note)
    if line > line_last:
        raise NoCodeThere(path, line)

    for i, (line_start, line_end) in enumerate(
        it.pairwise([ch.line_number for ch in doc.children] + [line_last + 1])
    ):
        if line >= line_start and line < line_end:
            snippet = doc.children[i]
            break
    else:
        raise RuntimeError(
            f"Supposed to be able to find a snippet in file {path}, at line {line}. "
            "Concurrent modification?"
        )

    if not isinstance(snippet, (BlockCode, CodeFence)):
        raise NoCodeThere(path, line)
    assert snippet.language in {"", "python"}
    return snippet.content.rstrip() + "\n", -1


@dataclass
class NoCodeThere(Exception):
    path: Path
    line: int
