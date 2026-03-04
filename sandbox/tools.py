from pathlib import Path


def _sandbox_root() -> Path:
    return Path("sandbox/runtime").resolve()


def _safe_path(path: str = ".") -> Path:
    root = _sandbox_root()
    target = (root / path).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError("Path must stay inside sandbox runtime")
    return target


def sandbox_status() -> dict:
    root = _sandbox_root()
    return {
        "sandbox_root": str(root),
        "exists": root.exists(),
    }


def sandbox_list_files(path: str = ".", recursive: bool = True) -> list[str]:
    target = _safe_path(path)
    if not target.exists():
        return []

    if target.is_file():
        return [str(target.relative_to(_sandbox_root()))]

    pattern = "**/*" if recursive else "*"
    return sorted(
        str(item.relative_to(_sandbox_root()))
        for item in target.glob(pattern)
        if item.is_file()
    )


def sandbox_read_file(path: str) -> str:
    target = _safe_path(path)
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return target.read_text(encoding="utf-8")


def sandbox_write_file(path: str, content: str, overwrite: bool = True) -> str:
    target = _safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {path}")

    target.write_text(content, encoding="utf-8")
    return str(target.relative_to(_sandbox_root()))


def sandbox_create_directory(path: str) -> str:
    target = _safe_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return str(target.relative_to(_sandbox_root()))


def sandbox_delete_path(path: str, missing_ok: bool = True) -> bool:
    target = _safe_path(path)
    if not target.exists():
        return missing_ok

    if target.is_file():
        target.unlink()
    else:
        for child in sorted(target.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
            else:
                child.rmdir()
        target.rmdir()
    return True
