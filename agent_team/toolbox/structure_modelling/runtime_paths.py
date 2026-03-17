import os
from pathlib import Path


def _settings_sandbox_root() -> Path | None:
    try:
        import settings as settings_module
    except Exception:
        return None

    configured = Path(settings_module.settings.SANDBOX_DIR).expanduser()
    if configured.is_absolute():
        return configured.resolve()

    project_root = Path(settings_module.__file__).resolve().parent
    return (project_root / configured).resolve()


def sandbox_root() -> Path:
    override = os.environ.get("ATOMSCULPTOR_SANDBOX_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    configured = _settings_sandbox_root()
    if configured is not None:
        return configured

    return Path(".").resolve()


def sandbox_output_dir() -> Path:
    output_dir = sandbox_root()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def display_path(path: Path) -> str:
    resolved = path.expanduser().resolve()
    root = sandbox_root()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(resolved)


def resolve_output_path(output_name: str) -> Path:
    output_path = Path(output_name)
    if not output_path.is_absolute():
        output_path = sandbox_output_dir() / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path