import sys
from pathlib import Path


_RUNTIME_TOOLBOX_GROUPS = {
    "structure_modelling": {
        "launchers": {
            "structure_tools.py": "agent_team.toolbox.structure_modelling.structure_tools",
            "crystal_builder.py": "agent_team.toolbox.structure_modelling.crystal_builder",
        },
        "docs": ["doc.md"],
    },
}


def _launcher_script(module_name: str, runtime_root: Path, python_executable: Path) -> str:
    return (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import sys\n"
        "\n"
        f"os.environ.setdefault('ATOMSCULPTOR_SANDBOX_ROOT', {str(runtime_root)!r})\n"
        f"PYTHON_EXECUTABLE = {str(python_executable)!r}\n"
        f"MODULE_NAME = {module_name!r}\n"
        "os.execv(PYTHON_EXECUTABLE, [PYTHON_EXECUTABLE, '-m', MODULE_NAME, *sys.argv[1:]])\n"
    )


def _runtime_doc(source_doc: Path) -> str:
    header = (
        "# Runtime Toolbox Launchers\n\n"
        "These files are thin runtime launchers.\n"
        "The actual implementation lives in the installed AtomSculptor package under `agent_team.toolbox.structure_modelling`.\n\n"
    )
    return header + source_doc.read_text(encoding="utf-8")


def _copy_markdown_tree(source_dir: Path, target_dir: Path) -> None:
    if not source_dir.exists():
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    for source_file in source_dir.rglob("*.md"):
        if not source_file.is_file():
            continue
        target_file = target_dir / source_file.relative_to(source_dir)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")


def materialize_runtime_toolbox(runtime_dir: str | Path, python_executable: str | Path | None = None) -> None:
    runtime_root = Path(runtime_dir).expanduser().resolve()
    runtime_toolbox_dir = runtime_root / "toolbox"
    runtime_toolbox_dir.mkdir(parents=True, exist_ok=True)

    source_toolbox_dir = Path(__file__).resolve().parent.parent / "agent_team" / "toolbox"
    source_instructions_dir = Path(__file__).resolve().parent.parent / "agent_team" / "memories" / "instructions"
    launcher_python = Path(python_executable or sys.executable).expanduser()

    for group_name, group in _RUNTIME_TOOLBOX_GROUPS.items():
        group_dir = runtime_toolbox_dir / group_name
        group_dir.mkdir(parents=True, exist_ok=True)

        for relative_file, module_name in group["launchers"].items():
            target = group_dir / relative_file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                _launcher_script(module_name, runtime_root, launcher_python),
                encoding="utf-8",
            )

        for doc_name in group.get("docs", []):
            source_doc = source_toolbox_dir / group_name / doc_name
            runtime_doc = group_dir / doc_name
            runtime_doc.parent.mkdir(parents=True, exist_ok=True)
            runtime_doc.write_text(_runtime_doc(source_doc), encoding="utf-8")

    _copy_markdown_tree(source_instructions_dir, runtime_root / "instructions")
