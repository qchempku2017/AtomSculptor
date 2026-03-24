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

## crystal_builder.py

Tool for generating common bulk crystal structures from scratch.

### Included Tools:

- `build_bulk_crystal`
- `list_crystal_structures`
