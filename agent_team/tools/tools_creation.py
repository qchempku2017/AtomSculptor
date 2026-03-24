"""Meta-tools for agents to create, validate, list, and promote sandbox CLI tools."""
import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

from settings import settings
from sandbox.toolbox_launchers import (
    CUSTOM_IMPL_SUFFIX,
    _SOURCE_TOOLBOX_DIR,
    _discover_default_tools,
    build_doc_content,
    build_impl_content,
    custom_launcher_script,
    discover_custom_tools,
    extract_public_function_names,
    materialize_runtime_toolbox,
)


def _runtime_root() -> Path:
    return Path(settings.SANDBOX_DIR).expanduser().resolve()


def _runtime_toolbox_dir() -> Path:
    return _runtime_root() / "toolbox"


def _python_executable() -> Path:
    return Path(sys.executable).expanduser()


# ---------------------------------------------------------------------------
# Meta-tools exposed to agents
# ---------------------------------------------------------------------------

def create_toolbox_tool(group: str, tool_name: str, description: str, code: str) -> dict:
    """Create a new CLI tool in the sandbox toolbox.

    Parameters:
    - group: Toolbox group name (e.g. "analysis").  Created if it doesn't exist.
    - tool_name: Tool name without the .py extension (e.g. "geometry_tools").
    - description: One-line description of the tool module.
    - code: Python source code containing import statements and tool function
      definitions.  Every public function (name not starting with ``_``) becomes
      a CLI sub-command.  Each function must accept simple typed parameters
      (str, int, float, bool, list, dict) and return a ``dict`` result.

      The following helpers from the sandbox runtime are available to import
      inside the code (they are auto-included at the top of the generated file):
        - ``sandbox_root()``         – root path of the sandbox
        - ``sandbox_output_dir()``   – default output directory
        - ``resolve_output_path(name)`` – resolve an output file name
        - ``display_path(path)``     – sandbox-relative display path

    Returns a dict with the paths of the generated files on success, or an
    ``error`` key on failure.
    """
    # Validate inputs
    if not group or not group.replace("_", "").isalnum():
        return {"error": f"Invalid group name: {group!r}"}
    if not tool_name or not tool_name.replace("_", "").isalnum():
        return {"error": f"Invalid tool name: {tool_name!r}"}

    # Parse the user code to extract public function names
    try:
        function_names = extract_public_function_names(code)
    except SyntaxError as exc:
        return {"error": f"Syntax error in provided code: {exc}"}

    if not function_names:
        return {"error": "No public functions found in the provided code. "
                "Functions must be top-level and not start with '_'."}

    # Build the implementation file content
    impl_content = build_impl_content(tool_name, description, code, function_names)

    # Validate the generated module parses correctly
    try:
        ast.parse(impl_content)
    except SyntaxError as exc:
        return {"error": f"Generated implementation has a syntax error: {exc}"}

    # Build the launcher and doc
    runtime_root = _runtime_root()
    group_dir = _runtime_toolbox_dir() / group
    group_dir.mkdir(parents=True, exist_ok=True)

    impl_filename = f"{tool_name}{CUSTOM_IMPL_SUFFIX}"
    launcher_content = custom_launcher_script(impl_filename, runtime_root, _python_executable())
    doc_content = build_doc_content(tool_name, group, description, function_names)

    # Write all three files
    impl_path = group_dir / impl_filename
    launcher_path = group_dir / f"{tool_name}.py"
    doc_path = group_dir / f"{tool_name}_doc.md"

    impl_path.write_text(impl_content, encoding="utf-8")
    launcher_path.write_text(launcher_content, encoding="utf-8")
    doc_path.write_text(doc_content, encoding="utf-8")

    tool_cli_path = f"toolbox/{group}/{tool_name}.py"
    return {
        "tool_cli_path": tool_cli_path,
        "functions": function_names,
        "files_created": [
            f"toolbox/{group}/{impl_filename}",
            f"toolbox/{group}/{tool_name}.py",
            f"toolbox/{group}/{tool_name}_doc.md",
        ],
        "usage_hint": f"python3 {tool_cli_path} -h",
    }


def list_toolbox_tools() -> dict:
    """List all tools available in the sandbox toolbox (default and custom).

    Returns a dict with separate ``default_tools`` and ``custom_tools`` sections.
    """
    runtime_root = _runtime_root()

    # Default tools (from agent_team/toolbox)
    default = _discover_default_tools()
    default_section: dict[str, list[str]] = {}
    for group_name, launchers in default.items():
        default_section[group_name] = [
            Path(filename).stem for filename in launchers
        ]

    # Custom tools (from runtime sandbox)
    custom_section = discover_custom_tools(runtime_root)

    return {
        "default_tools": default_section,
        "custom_tools": custom_section,
    }


def validate_toolbox_tool(group: str, tool_name: str) -> dict:
    """Validate a toolbox tool by running its ``--help`` in a subprocess.

    Returns the help output on success, or an error message.
    """
    launcher_path = _runtime_toolbox_dir() / group / f"{tool_name}.py"
    if not launcher_path.exists():
        return {"error": f"Tool not found: toolbox/{group}/{tool_name}.py"}

    try:
        env = os.environ.copy()
        env["ATOMSCULPTOR_SANDBOX_ROOT"] = str(_runtime_root())
        result = subprocess.run(
            [str(_python_executable()), str(launcher_path), "-h"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(_runtime_root()),
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"error": "Tool timed out while running --help"}

    if result.returncode != 0:
        return {
            "error": "Tool exited with non-zero status",
            "stderr": result.stderr.strip(),
            "stdout": result.stdout.strip(),
        }

    return {
        "valid": True,
        "help_output": result.stdout.strip(),
    }


def promote_toolbox_tool(group: str, tool_name: str) -> dict:
    """Promote a custom sandbox tool into the default toolbox.

    Copies the implementation and doc files from the sandbox runtime into
    ``agent_team/toolbox/{group}/`` so the tool becomes a permanent part of
    the package.  On the next ``materialize_runtime_toolbox`` call, a proper
    module launcher will replace the custom launcher.

    Returns a dict describing what was copied, or an ``error`` key.
    """
    impl_path = _runtime_toolbox_dir() / group / f"{tool_name}{CUSTOM_IMPL_SUFFIX}"
    doc_path = _runtime_toolbox_dir() / group / f"{tool_name}_doc.md"

    if not impl_path.exists():
        return {"error": f"Custom tool implementation not found: {impl_path.name}"}

    target_group_dir = _SOURCE_TOOLBOX_DIR / group
    target_group_dir.mkdir(parents=True, exist_ok=True)

    target_impl = target_group_dir / f"{tool_name}.py"
    target_doc = target_group_dir / f"{tool_name}_doc.md"

    if target_impl.exists():
        return {"error": f"A default tool already exists at {target_impl.relative_to(_SOURCE_TOOLBOX_DIR.parent.parent)}. "
                "Remove it first or choose a different name."}

    # Copy impl → default toolbox (dropping the _impl suffix)
    shutil.copy2(impl_path, target_impl)
    copied = [str(target_impl.relative_to(_SOURCE_TOOLBOX_DIR.parent.parent))]

    if doc_path.exists():
        shutil.copy2(doc_path, target_doc)
        copied.append(str(target_doc.relative_to(_SOURCE_TOOLBOX_DIR.parent.parent)))

    # Re-materialize so the promoted tool gets a proper module launcher
    materialize_runtime_toolbox(_runtime_root())

    # Clean up the custom _impl.py (now superseded by the module launcher)
    impl_path.unlink(missing_ok=True)

    return {
        "promoted": True,
        "files_copied": copied,
        "note": "The tool is now part of the default toolbox. "
                "Re-materialization replaced the custom launcher with a module launcher.",
    }
