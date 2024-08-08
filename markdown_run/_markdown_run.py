from dataclasses import dataclass
import io
from mistletoe import Document  # type: ignore
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

    assert len(doc.children) == 1
    snippet = doc.children[0]
    assert snippet.language in {"", "python"}
    return snippet.content.rstrip() + "\n"


@dataclass
class NoCodeThere(Exception):
    path: Path
    line: int
