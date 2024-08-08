import io
from mistletoe import Document  # type: ignore
import os
from pathlib import Path
from typing import Union


def extract_code(path: Union[os.PathLike, Path], line: int) -> str:
    with Path(path).open(mode="r", encoding="utf-8") as file:
        doc = Document(file)
    assert len(doc.children) == 1
    snippet = doc.children[0]
    assert snippet.language in {"", "python"}
    return snippet.content.rstrip() + "\n"
