"""Deprecated compatibility wrappers for structure tools."""

from agent_team.toolbox.structure_modelling.structure_tools import (
    build_interface,
    build_supercell,
    build_surface,
    calculate_distance,
    check_close_atoms,
    generate_structure_image,
    read_structure,
    read_structures_in_text,
)


__all__ = [
    "read_structure",
    "read_structures_in_text",
    "calculate_distance",
    "build_supercell",
    "build_surface",
    "generate_structure_image",
    "check_close_atoms",
    "build_interface",
]

