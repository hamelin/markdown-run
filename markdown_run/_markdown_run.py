from dataclasses import dataclass
import itertools as it
from mistletoe import Document  # type: ignore
from mistletoe.block_token import BlockCode, CodeFence  # type: ignore
import os
from pathlib import Path
from typing import Union


def extract_code(path_: Union[os.PathLike[str], str], line: int) -> str:
    assert line >= 0
    path = Path(path_)
    with path.open(mode="r", encoding="utf-8") as file:
        doc = Document(file)
    if not doc.children:
        raise NoCodeThere(path, line)
    last_line = len(path.read_text().split("\n"))
    if line > last_line:
        raise NoCodeThere(path, line)

    for i, (line_start, line_end) in enumerate(
        it.pairwise([ch.line_number for ch in doc.children] + [last_line + 1])
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
    return snippet.content.rstrip() + "\n"


@dataclass
class NoCodeThere(Exception):
    path: Path
    line: int
