import ast
import sys
from pathlib import Path


_SOURCE_TOOLBOX_DIR = Path(__file__).resolve().parent.parent / "agent_team" / "toolbox"
_SOURCE_INSTRUCTIONS_DIR = Path(__file__).resolve().parent.parent / "agent_team" / "memories" / "instructions"

# Suffix used to identify custom tool implementation files in the runtime toolbox.
CUSTOM_IMPL_SUFFIX = "_impl.py"


def _discover_default_tools() -> dict[str, dict[str, str]]:
    """Auto-discover default tools from ``agent_team/toolbox/*/``.

    Returns ``{group_name: {filename: module_name}}``.
    """
    groups: dict[str, dict[str, str]] = {}
    if not _SOURCE_TOOLBOX_DIR.is_dir():
        return groups
    for group_dir in sorted(_SOURCE_TOOLBOX_DIR.iterdir()):
        if not group_dir.is_dir() or group_dir.name.startswith(("_", ".")):
            continue
        launchers: dict[str, str] = {}
        for py_file in sorted(group_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            module_name = f"agent_team.toolbox.{group_dir.name}.{py_file.stem}"
            launchers[py_file.name] = module_name
        if launchers:
            groups[group_dir.name] = launchers
    return groups


def _launcher_script(module_name: str, runtime_root: Path, python_executable: Path) -> str:
    """Launcher that delegates to an installed package module via ``-m``."""
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


def custom_launcher_script(impl_filename: str, runtime_root: Path, python_executable: Path) -> str:
    """Launcher that delegates to a custom tool implementation script."""
    return (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "import sys\n"
        "\n"
        f"os.environ.setdefault('ATOMSCULPTOR_SANDBOX_ROOT', {str(runtime_root)!r})\n"
        f"PYTHON_EXECUTABLE = {str(python_executable)!r}\n"
        f"IMPL_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), {impl_filename!r})\n"
        "os.execv(PYTHON_EXECUTABLE, [PYTHON_EXECUTABLE, IMPL_SCRIPT, *sys.argv[1:]])\n"
    )


def _runtime_doc(source_doc: Path) -> str:
    header = (
        "# Runtime Toolbox Launchers\n\n"
        "These files are thin runtime launchers.\n"
        "The actual implementation lives in the installed AtomSculptor package under `agent_team.toolbox`.\n\n"
    )
    return header + source_doc.read_text(encoding="utf-8")


def _doc_name_for_tool(stem: str) -> str:
    return f"{stem}_doc.md"


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


def extract_public_function_names(code: str) -> list[str]:
    """Parse *code* and return names of top-level public ``def`` statements."""
    tree = ast.parse(code)
    return [
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]


def build_impl_content(tool_name: str, description: str, user_code: str, function_names: list[str]) -> str:
    """Produce a complete CLI tool module from user-supplied function code."""
    lines: list[str] = []
    lines.append(f'"""{description}"""')
    lines.append("from sandbox.cli_support import build_cli_parser, run_cli")
    lines.append("from sandbox.runtime_paths import (")
    lines.append("    display_path,")
    lines.append("    resolve_output_path,")
    lines.append("    sandbox_output_dir,")
    lines.append("    sandbox_root,")
    lines.append(")")
    lines.append("")
    lines.append("")
    lines.append(user_code.rstrip())
    lines.append("")
    lines.append("")
    lines.append(f"TOOL_FUNCTION_NAMES = {function_names!r}")
    lines.append("")
    lines.append("")
    lines.append("def _tool_functions():")
    lines.append("    return {name: globals()[name] for name in TOOL_FUNCTION_NAMES}")
    lines.append("")
    lines.append("")
    lines.append("def _build_cli_parser():")
    lines.append("    return build_cli_parser(")
    lines.append(f'        prog="{tool_name}.py",')
    lines.append("        description_lines=[")
    lines.append(f'            "{description}",')
    lines.append('            f"Working directory: {sandbox_root()}",')
    lines.append('            "",')
    lines.append("        ],")
    lines.append("        tool_functions=_tool_functions(),")
    lines.append("    )")
    lines.append("")
    lines.append("")
    lines.append("def _run_cli(argv=None):")
    lines.append("    return run_cli(")
    lines.append("        argv=argv,")
    lines.append("        parser=_build_cli_parser(),")
    lines.append("        tool_functions=_tool_functions(),")
    lines.append("    )")
    lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    raise SystemExit(_run_cli())")
    lines.append("")
    return "\n".join(lines)


def build_doc_content(tool_name: str, group: str, description: str, function_names: list[str]) -> str:
    """Generate a ``_doc.md`` file for a custom tool."""
    tool_path = f"toolbox/{group}/{tool_name}.py"
    func_list = "\n".join(f"- `{n}`" for n in function_names)
    return (
        f"# {tool_name} CLI\n\n"
        f"{description}\n\n"
        "The CLI tools have two help layers:\n\n"
        f"- General help: `python3 {tool_path} -h`\n"
        f"- Tool-specific help: `python3 {tool_path} <tool_name> -h`\n\n"
        "## How To Use\n\n"
        "```bash\n"
        f"python3 {tool_path} -h\n"
        f"python3 {tool_path} <tool_name> -h\n"
        "```\n\n"
        f"## {tool_name}.py\n\n"
        f"{description}\n\n"
        "### Included Tools:\n\n"
        f"{func_list}\n"
    )


def discover_custom_tools(runtime_dir: str | Path) -> dict[str, list[str]]:
    """Discover custom tools in the runtime toolbox.

    Returns ``{group_name: [tool_name, ...]}``.
    """
    runtime_root = Path(runtime_dir).expanduser().resolve()
    runtime_toolbox_dir = runtime_root / "toolbox"
    if not runtime_toolbox_dir.is_dir():
        return {}
    groups: dict[str, list[str]] = {}
    for group_dir in sorted(runtime_toolbox_dir.iterdir()):
        if not group_dir.is_dir() or group_dir.name.startswith(("_", ".")):
            continue
        tools: list[str] = []
        for impl_file in sorted(group_dir.glob(f"*{CUSTOM_IMPL_SUFFIX}")):
            tool_name = impl_file.stem.removesuffix("_impl")
            tools.append(tool_name)
        if tools:
            groups[group_dir.name] = tools
    return groups


def materialize_runtime_toolbox(runtime_dir: str | Path, python_executable: str | Path | None = None) -> None:
    """Write default-tool launchers and docs into the runtime sandbox.

    Custom tools (``*_impl.py``) in the runtime are never touched.
    """
    runtime_root = Path(runtime_dir).expanduser().resolve()
    runtime_toolbox_dir = runtime_root / "toolbox"
    runtime_toolbox_dir.mkdir(parents=True, exist_ok=True)

    launcher_python = Path(python_executable or sys.executable).expanduser()
    default_tools = _discover_default_tools()

    for group_name, launchers in default_tools.items():
        group_dir = runtime_toolbox_dir / group_name
        group_dir.mkdir(parents=True, exist_ok=True)

        for relative_file, module_name in launchers.items():
            target = group_dir / relative_file
            target.write_text(
                _launcher_script(module_name, runtime_root, launcher_python),
                encoding="utf-8",
            )

            doc_name = _doc_name_for_tool(Path(relative_file).stem)
            source_doc = _SOURCE_TOOLBOX_DIR / group_name / doc_name
            if source_doc.exists():
                runtime_doc = group_dir / doc_name
                runtime_doc.write_text(_runtime_doc(source_doc), encoding="utf-8")

    _copy_markdown_tree(_SOURCE_INSTRUCTIONS_DIR, runtime_root / "instructions")
