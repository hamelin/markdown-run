import io
from mistletoe import Document  # type: ignore


def extract_code(file: io.TextIOBase, line: int) -> str:
    doc = Document(file)
    assert len(doc.children) == 1
    snippet = doc.children[0]
    assert snippet.language in {"", "python"}
    return snippet.content.rstrip() + "\n"
