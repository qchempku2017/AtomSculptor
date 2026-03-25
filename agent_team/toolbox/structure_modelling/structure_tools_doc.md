# Structure Tools CLI

This module provides CLI tools for working with atomic structures directly inside the runtime sandbox.

The CLI tools have two help layers:

- General help: `python3 path/to/tools.py -h`
- Tool-specific help: `python3 path/to/tools.py <tool_name> -h`

## How To Use

```bash
python3 path/to/tools.py -h
python3 path/to/tools.py <tool_name> -h
```

Notes:

- Relative input paths are resolved against the current working directory.
- Output files are written into the current working directory unless you pass an absolute path.
- List and tuple parameters must be passed as JSON strings, for example `'[2, 2, 1]'` or `'[1, 0, 0]'`.
- Boolean parameters should be passed explicitly, for example `--in-layers true`.
- CLI results are printed as JSON. If the tool returns an `error` field, the CLI exits with a non-zero status.

---

## structure_tools.py

Tools for reading, manipulating, and analyzing existing structure files.

### Included Tools:

- `read_structure`
- `read_structures_in_text`
- `calculate_distance`
- `build_supercell`
- `build_surface`
- `generate_structure_image`
- `check_close_atoms`
- `build_interface`

