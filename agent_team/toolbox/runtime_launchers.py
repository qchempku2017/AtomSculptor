import sys
from pathlib import Path


_LAUNCHERS = {
    "structure_modelling/structure_tools.py": "agent_team.toolbox.structure_modelling.structure_tools",
    "structure_modelling/crystal_builder.py": "agent_team.toolbox.structure_modelling.crystal_builder",
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


def materialize_runtime_toolbox(runtime_dir: str | Path, python_executable: str | Path | None = None) -> None:
    runtime_root = Path(runtime_dir).expanduser().resolve()
    runtime_toolbox_dir = runtime_root / "toolbox"
    runtime_toolbox_dir.mkdir(parents=True, exist_ok=True)

    launcher_python = Path(python_executable or sys.executable).expanduser()

    for relative_path, module_name in _LAUNCHERS.items():
        target = runtime_toolbox_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            _launcher_script(module_name, runtime_root, launcher_python),
            encoding="utf-8",
        )

    source_doc = Path(__file__).resolve().parent / "structure_modelling" / "doc.md"
    runtime_doc = runtime_toolbox_dir / "structure_modelling" / "doc.md"
    runtime_doc.parent.mkdir(parents=True, exist_ok=True)
    runtime_doc.write_text(_runtime_doc(source_doc), encoding="utf-8")