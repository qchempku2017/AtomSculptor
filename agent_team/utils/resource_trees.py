from pathlib import Path


def directory_tree(root: Path, max_depth: int = 3, max_entries: int = 200) -> str:
    """Return an ASCII tree for a directory with sensible size limits."""
    if not root.exists():
        return f"{root.name}/ (not found)"
    if not root.is_dir():
        return f"{root.name} (not a directory)"

    lines: list[str] = [f"{root.name}/"]
    entries_count = 0

    def _walk(path: Path, prefix: str, depth: int) -> None:
        nonlocal entries_count
        if depth > max_depth or entries_count >= max_entries:
            return

        children = sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        children = [child for child in children if child.name != "__pycache__"]

        for index, child in enumerate(children):
            if entries_count >= max_entries:
                lines.append(prefix + "- ...")
                return

            is_last = index == len(children) - 1
            suffix = "/" if child.is_dir() else ""
            lines.append(prefix + "- " + child.name + suffix)
            entries_count += 1

            if child.is_dir() and depth < max_depth:
                extension = "    " if is_last else "|   "
                _walk(child, prefix + extension, depth + 1)

    try:
        _walk(root, "", 1)
    except OSError as exc:
        lines.append(f"- <error reading directory: {exc}>")

    return "\n".join(lines)


def build_resource_trees(
    runtime_root: Path,
    toolbox_path: str = "toolbox/",
    instructions_path: str = "instructions/",
) -> str:
    toolbox_dir = runtime_root / toolbox_path
    instructions_dir = runtime_root / instructions_path
    return f"{directory_tree(toolbox_dir)}\n\n{directory_tree(instructions_dir)}"
