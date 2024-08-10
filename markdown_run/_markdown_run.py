from dataclasses import dataclass
import itertools as it
from mistletoe import Document, HTMLRenderer  # type: ignore
from mistletoe.block_token import CodeFence  # type: ignore
import os
from pathlib import Path
import re
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

    if not isinstance(snippet, CodeFence):
        raise NoCodeThere(path, line)
    assert snippet.language in {"", "python"}

    # Output should be inserted right after the closing fence of the code.
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
    line_output = i_output + 1

    return snippet.content.rstrip() + "\n", line_output


@dataclass
class NoCodeThere(Exception):
    path: Path
    line: int
