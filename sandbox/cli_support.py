import argparse
import inspect
import json
from types import NoneType, UnionType
from typing import Any, Callable, Union, get_args, get_origin


def parse_json_or_raw(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "f", "no", "n", "off"}:
            return False
    raise ValueError(f"Expected a boolean value, got: {value!r}")


def annotation_to_cli_type(annotation: Any) -> str:
    origin = get_origin(annotation)

    if annotation in (inspect._empty, Any, str):
        return "string"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"
    if annotation in (list, tuple, dict):
        return "JSON"
    if origin in (list, tuple, dict):
        return "JSON"
    if origin in (UnionType, Union):
        args = [arg for arg in get_args(annotation) if arg is not NoneType]
        if len(args) == 1:
            return annotation_to_cli_type(args[0])
        cli_types = {annotation_to_cli_type(arg) for arg in args}
        if len(cli_types) == 1:
            return cli_types.pop()
    return "string"


def coerce_cli_value(raw_value: str, annotation: Any) -> Any:
    origin = get_origin(annotation)

    if annotation in (inspect._empty, Any, str):
        return raw_value
    if annotation is int:
        return int(raw_value)
    if annotation is float:
        return float(raw_value)
    if annotation is bool:
        return parse_bool(raw_value)
    if annotation is list:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list, got: {raw_value}")
        return parsed
    if annotation is tuple:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list for tuple input, got: {raw_value}")
        return tuple(parsed)
    if annotation is dict:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected a JSON object, got: {raw_value}")
        return parsed
    if origin is list:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list, got: {raw_value}")
        return parsed
    if origin is tuple:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list for tuple input, got: {raw_value}")
        return tuple(parsed)
    if origin is dict:
        parsed = parse_json_or_raw(raw_value)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected a JSON object, got: {raw_value}")
        return parsed
    if origin in (UnionType, Union):
        args = [arg for arg in get_args(annotation) if arg is not NoneType]
        last_error: Exception | None = None
        for arg in args:
            try:
                return coerce_cli_value(raw_value, arg)
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise ValueError(str(last_error)) from last_error
    return parse_json_or_raw(raw_value)


_SECTION_HEADERS = {"args:", "arguments:", "parameters:", "returns:", "return:", "raises:", "note:", "notes:"}


def _parse_param_docs(doc: str, param_names: set[str]) -> dict[str, str]:
    """Extract per-parameter descriptions from a docstring.

    Recognises two styles:
      Google-style ``Args:`` / ``Parameters:`` sections with indented entries:
          param_name: description text
      Bullet-style lines (with optional leading dash):
          - param_name: description text
          - param_name is description text
    """
    result: dict[str, str] = {}
    lines = doc.splitlines()
    in_args_section = False

    for line in lines:
        lower = line.strip().lower()
        if lower in _SECTION_HEADERS:
            in_args_section = lower in {"args:", "arguments:", "parameters:"}
            continue
        if in_args_section and line.strip() == "":
            in_args_section = False
            continue

        if in_args_section:
            # Google-style:  "    param_name: description"
            # or with bullet: "    - param_name: description"
            stripped = line.strip().lstrip("- ").strip()
            for name in param_names:
                if stripped.startswith(name + ":"):
                    result[name] = stripped[len(name) + 1:].strip()
                    break
        else:
            # Bullet-style: "- param_name: ..." or "- param_name is ..."
            stripped = line.strip().lstrip("- ").strip()
            for name in param_names:
                if stripped.startswith(name + ":"):
                    result[name] = stripped[len(name) + 1:].strip()
                    break
                if stripped.startswith(name + " is "):
                    result[name] = stripped[len(name) + 4:].strip()
                    break

    return result


def _strip_param_lines(doc: str, param_names: set[str]) -> str:
    """Remove per-parameter lines and section headers from a docstring.

    Strips:
    - Google-style section blocks (Args:, Parameters:, Returns:, etc.) and all
      their indented content.
    - Bullet-style param lines outside sections that match a known param name.

    The result is suitable for use as a command description.
    """
    lines = doc.splitlines()
    result: list[str] = []
    in_section = False

    for line in lines:
        lower = line.strip().lower()
        if lower in _SECTION_HEADERS:
            in_section = True
            continue
        if in_section:
            if line.strip() == "":
                in_section = False
            continue  # skip all content inside any section block

        # Outside sections: skip bullet-style param lines
        bare = line.strip().lstrip("- ").strip()
        if any(bare.startswith(name + ":") or bare.startswith(name + " is ") for name in param_names):
            continue

        result.append(line)

    # Strip trailing blank lines
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result)


def build_cli_parser(
    *,
    prog: str,
    description_lines: list[str],
    tool_functions: dict[str, Callable[..., Any]],
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="\n".join(description_lines),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="tool_name", metavar="tool_name")

    for tool_name, function in tool_functions.items():
        tool_doc = inspect.getdoc(function) or ""
        sig = inspect.signature(function)
        param_docs = _parse_param_docs(tool_doc, set(sig.parameters))
        clean_doc = _strip_param_lines(tool_doc, set(sig.parameters))

        tool_parser = subparsers.add_parser(
            tool_name,
            help=clean_doc.splitlines()[0] if clean_doc else tool_name,
            description=clean_doc,
            formatter_class=argparse.RawTextHelpFormatter,
        )

        sig = inspect.signature(function)
        param_docs = _parse_param_docs(tool_doc, set(sig.parameters))

        for parameter in sig.parameters.values():
            cli_flag = f"--{parameter.name.replace('_', '-')}"
            cli_type = annotation_to_cli_type(parameter.annotation)
            desc = param_docs.get(parameter.name, "")
            help_text = f"({cli_type}) {desc}".rstrip() if desc else f"({cli_type})"
            if parameter.default is not inspect._empty:
                help_text += f"  [default: {parameter.default!r}]"
            if cli_type == "JSON":
                help_text += "  e.g. '[1, 0, 0]'"

            tool_parser.add_argument(
                cli_flag,
                dest=parameter.name,
                required=parameter.default is inspect._empty,
                help=help_text,
            )

        tool_parser.epilog = (
            "Examples:\n"
            f"  python3 {prog} {tool_name} --help\n"
            f"  python3 {prog} {tool_name} "
            + " ".join(
                f"--{p.name.replace('_', '-')} <{annotation_to_cli_type(p.annotation)}>"
                for p in sig.parameters.values()
            )
        )

    return parser


def run_cli(
    *,
    argv: list[str] | None,
    parser: argparse.ArgumentParser,
    tool_functions: dict[str, Callable[..., Any]],
) -> int:
    args = parser.parse_args(argv)

    if not getattr(args, "tool_name", None):
        parser.print_help()
        return 0

    function = tool_functions[args.tool_name]
    signature = inspect.signature(function)

    try:
        kwargs = {}
        for parameter in signature.parameters.values():
            raw_value = getattr(args, parameter.name)
            if raw_value is None:
                continue
            kwargs[parameter.name] = coerce_cli_value(raw_value, parameter.annotation)
    except Exception as exc:
        parser.error(str(exc))

    result = function(**kwargs)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not isinstance(result, dict) or "error" not in result else 1
