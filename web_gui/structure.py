"""ASE and layered-LXYZ structure detection, parsing, and serialisation."""

from __future__ import annotations

import re
from pathlib import Path

STRUCTURE_EXTS = {"cif", "xyz", "vasp", "poscar", "extxyz", "pdb", "sdf", "mol2", "lxyz"}
VASP_STRUCTURE_PREFIXES = ("poscar", "contcar")

_LATTICE_SECTION_RE = re.compile(r"^\[\s*lattice\s+layer\s*\]$", re.IGNORECASE)
_ATOMS_SECTION_RE = re.compile(r"^\[\s*<?\s*atoms\s+layer\s+(\d+)\s*>?\s*\]$", re.IGNORECASE)
_KV_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("[^"]*"|[^\s]+)')


def _identity_cell() -> list[list[float]]:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def _flatten_cell(cell: list[list[float]] | None) -> str:
    mat = cell if isinstance(cell, list) and len(cell) == 3 else _identity_cell()
    nums = [mat[i][j] for i in range(3) for j in range(3)]
    return " ".join(f"{float(v):.6f}" for v in nums)


def _parse_lattice_numbers(line: str) -> list[list[float]]:
    parts = line.split()
    if len(parts) != 9:
        raise ValueError("lattice layer line must contain exactly 9 numbers")
    nums = [float(p) for p in parts]
    return [nums[0:3], nums[3:6], nums[6:9]]


def _cell_has_magnitude(cell: list[list[float]] | None) -> bool:
    if not isinstance(cell, list) or len(cell) != 3:
        return False
    return any(abs(float(v)) > 1e-12 for row in cell for v in row)


def _parse_extxyz_like_meta(meta_line: str) -> tuple[list[list[float]] | None, list[bool] | None]:
    if not meta_line:
        return None, None
    found = {k: v for k, v in _KV_RE.findall(meta_line)}

    cell = None
    pbc = None

    lattice_val = found.get("Lattice") or found.get("lattice")
    if lattice_val:
        raw = lattice_val.strip().strip('"')
        vals = raw.split()
        if len(vals) == 9:
            nums = [float(x) for x in vals]
            cell = [nums[0:3], nums[3:6], nums[6:9]]

    pbc_val = found.get("pbc") or found.get("PBC")
    if pbc_val:
        raw = pbc_val.strip().strip('"').lower()
        if raw in {"t t t", "true true true"}:
            pbc = [True, True, True]
        elif raw in {"f f f", "false false false"}:
            pbc = [False, False, False]
        else:
            bits = raw.split()
            if len(bits) == 3:
                pbc = [b in {"t", "true", "1", "yes"} for b in bits]

    return cell, pbc


def _read_lxyz_structure(fp: Path) -> dict:
    text = fp.read_text(encoding="utf-8")
    lines = text.splitlines()

    base_cell = None
    base_pbc = [False, False, False]
    layers: list[dict] = []
    atoms: list[dict] = []

    current_layer: dict | None = None
    in_lattice = False
    next_atom_id = 0

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if _LATTICE_SECTION_RE.match(line):
            in_lattice = True
            current_layer = None
            continue

        atoms_match = _ATOMS_SECTION_RE.match(line)
        if atoms_match:
            in_lattice = False
            idx = int(atoms_match.group(1))
            layer_id = f"atoms-{idx}"
            current_layer = {
                "id": layer_id,
                "type": "atoms",
                "name": f"Atoms {idx}",
                "cell": None,
                "pbc": None,
                "meta": "",
            }
            layers.append(current_layer)
            continue

        if in_lattice:
            base_cell = _parse_lattice_numbers(line)
            in_lattice = False
            continue

        if current_layer is None:
            continue

        if not current_layer["meta"]:
            maybe_cell, maybe_pbc = _parse_extxyz_like_meta(line)
            if maybe_cell is not None or maybe_pbc is not None or "=" in line:
                current_layer["meta"] = line
                if maybe_cell is not None:
                    current_layer["cell"] = maybe_cell
                if maybe_pbc is not None:
                    current_layer["pbc"] = maybe_pbc
                continue

        parts = line.split()
        if len(parts) < 4:
            continue
        symbol = parts[0]
        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        atoms.append({
            "id": next_atom_id,
            "symbol": symbol,
            "x": x,
            "y": y,
            "z": z,
            "layerId": current_layer["id"],
        })
        next_atom_id += 1

    if base_cell is None:
        base_cell = _identity_cell()

    lattice_layer = {
        "id": "lattice",
        "type": "lattice",
        "name": "Lattice",
        "cell": base_cell,
        "pbc": base_pbc,
    }

    for layer in layers:
        if not _cell_has_magnitude(layer.get("cell")):
            layer["cell"] = [row[:] for row in base_cell]
        if not isinstance(layer.get("pbc"), list) or len(layer["pbc"]) != 3:
            layer["pbc"] = list(base_pbc)

    return {
        "atoms": atoms,
        "cell": base_cell,
        "pbc": base_pbc,
        "layers": [lattice_layer, *layers],
    }


def _write_lxyz_structure(fp: Path, atoms_data: list, cell, pbc, layers: list | None) -> int:
    layer_list = list(layers or [])
    lattice_layer = next((l for l in layer_list if l.get("type") == "lattice"), None)
    atom_layers = [l for l in layer_list if l.get("type") == "atoms"]

    base_cell = lattice_layer.get("cell") if lattice_layer else cell
    base_pbc = lattice_layer.get("pbc") if lattice_layer else pbc
    if not isinstance(base_pbc, list) or len(base_pbc) != 3:
        base_pbc = [False, False, False]

    if not atom_layers:
        atom_layers = [{"id": "atoms-1", "type": "atoms", "name": "Atoms 1", "cell": cell, "pbc": pbc}]

    grouped: dict[str, list[dict]] = {}
    for atom in atoms_data:
        lid = atom.get("layerId") or atom_layers[0]["id"]
        grouped.setdefault(lid, []).append(atom)

    out_lines: list[str] = ["[lattice layer]", _flatten_cell(base_cell)]

    def layer_index(layer_id: str) -> int:
        m = re.search(r"(\d+)$", str(layer_id))
        return int(m.group(1)) if m else 999999

    ordered_layers = sorted(atom_layers, key=lambda layer: layer_index(str(layer.get("id", ""))))
    fallback_meta = "Properties=species:S:1:pos:R:3"

    for index, layer in enumerate(ordered_layers, start=1):
        layer_id = str(layer.get("id", f"atoms-{index}"))
        out_lines.append(f"[<atoms layer {index}>]")

        layer_cell = layer.get("cell") if _cell_has_magnitude(layer.get("cell")) else base_cell
        layer_pbc = layer.get("pbc") if isinstance(layer.get("pbc"), list) and len(layer.get("pbc")) == 3 else base_pbc
        meta = layer.get("meta")
        if isinstance(meta, str) and meta.strip():
            out_lines.append(meta.strip())
        else:
            pbc_token = " ".join("T" if bool(v) else "F" for v in layer_pbc)
            out_lines.append(f"Lattice=\"{_flatten_cell(layer_cell)}\" pbc=\"{pbc_token}\" {fallback_meta}")

        for atom in grouped.get(layer_id, []):
            out_lines.append(
                f"{atom['symbol']} {float(atom['x']):.6f} {float(atom['y']):.6f} {float(atom['z']):.6f}"
            )

    fp.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return len(atoms_data)


def detect_ase_format(path_or_name: str | Path) -> str | None:
    name = Path(path_or_name).name.lower()
    suffix = Path(name).suffix.lower().lstrip(".")
    if suffix in STRUCTURE_EXTS:
        return "vasp" if suffix == "poscar" else suffix
    if any(
        name == prefix
        or name.startswith(f"{prefix}_")
        or name.startswith(f"{prefix}-")
        or name.startswith(f"{prefix}.")
        for prefix in VASP_STRUCTURE_PREFIXES
    ):
        return "vasp"
    return None


def resolve_ase_io_format(path: Path) -> str | None:
    """Resolve ASE format, including extxyz payload in .xyz files."""
    ase_format = detect_ase_format(path)
    if ase_format in {None, "lxyz"}:
        return ase_format
    if ase_format != "xyz":
        return ase_format

    try:
        with path.open("r", encoding="utf-8") as fh:
            _ = fh.readline()
            comment = fh.readline()
    except OSError:
        return ase_format

    lowered = comment.lower()
    if "lattice=" in lowered or "properties=" in lowered or "pbc=" in lowered:
        return "extxyz"
    return ase_format


def is_structure_filename(path_or_name: str | Path) -> bool:
    return detect_ase_format(path_or_name) is not None


def cell_to_json(atoms) -> list[list[float]] | None:
    """Return 3x3 cell matrix when structure defines a non-zero cell."""
    cell_obj = atoms.get_cell()
    if getattr(cell_obj, "rank", 0) <= 0:
        return None
    return cell_obj.tolist()


def read_structure(fp: Path) -> dict:
    """Read a structure file and return serialised atom/cell/pbc data."""
    detected = detect_ase_format(fp)
    if detected == "lxyz":
        return _read_lxyz_structure(fp)

    from ase.io import read as ase_read

    ase_format = resolve_ase_io_format(fp)
    atoms = ase_read(str(fp), format=ase_format)

    cell = cell_to_json(atoms)
    pbc = [bool(v) for v in atoms.get_pbc()]

    atom_list = []
    for i, atom in enumerate(atoms):
        atom_list.append({
            "id": i,
            "symbol": atom.symbol,
            "x": float(atom.position[0]),
            "y": float(atom.position[1]),
            "z": float(atom.position[2]),
        })

    return {"atoms": atom_list, "cell": cell, "pbc": pbc}


def write_structure(fp: Path, atoms_data: list, cell, pbc, layers: list | None = None) -> int:
    """Write atom data back to a structure file via ASE.  Returns atom count."""
    detected = detect_ase_format(fp)
    if detected == "lxyz":
        return _write_lxyz_structure(fp, atoms_data, cell, pbc, layers)

    from ase import Atoms as AseAtoms
    from ase.io import write as ase_write

    symbols = [a["symbol"] for a in atoms_data]
    positions = [[a["x"], a["y"], a["z"]] for a in atoms_data]
    kwargs = {"symbols": symbols, "positions": positions, "pbc": pbc}
    if cell is not None:
        kwargs["cell"] = cell
    new_atoms = AseAtoms(**kwargs)
    ase_format = resolve_ase_io_format(fp)
    if ase_format is None:
        ase_write(str(fp), new_atoms)
    else:
        ase_write(str(fp), new_atoms, format=ase_format)
    return len(atoms_data)
