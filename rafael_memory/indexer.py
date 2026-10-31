import argparse
import hashlib
import json
import re
from pathlib import Path


_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_MARKDOWN_SUFFIXES = {".md", ".markdown"}


def extract_structure(text: str) -> list[dict]:
    structure = []
    parents = []
    fence_character = None
    fence_length = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = _FENCE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue
        if fence_character is not None:
            continue

        heading_match = _HEADING.match(line)
        if not heading_match:
            continue

        level = len(heading_match.group(1))
        node = {
            "level": level,
            "title": heading_match.group(2).strip(),
            "line": line_number,
            "children": [],
        }
        while parents and parents[-1]["level"] >= level:
            parents.pop()
        if parents:
            parents[-1]["children"].append(node)
        else:
            structure.append(node)
        parents.append(node)

    return structure


def build_index(docs_dir: Path) -> dict:
    root = Path(docs_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Documentation directory not found: {root}")

    documents = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in _MARKDOWN_SUFFIXES:
            continue
        content = path.read_bytes()
        documents.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "structure": extract_structure(content.decode("utf-8", errors="replace")),
            }
        )

    return {"schema_version": 1, "documents": documents}


def write_index(docs_dir: Path, output_path: Path) -> dict:
    index = build_index(docs_dir)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Markdown documentation for the local memory store.")
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--output", type=Path, default=Path(".rafael/docs-index.json"))
    args = parser.parse_args()
    index = write_index(args.docs, args.output)
    print(f"Indexed {len(index['documents'])} document(s) to {args.output}")


if __name__ == "__main__":
    main()
