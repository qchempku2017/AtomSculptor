# Surface Creation Instructions

## Common Workflow

1. **Obtain bulk crystal structure**
   - **Option A: Materials Project search** (preferred for real materials)
     - Search by composition and stability (energy_above_hull=0 for most stable)
     - Download structure using Materials Project ID
   - **Option B: Manual creation** (when MP unavailable or for hypothetical structures)
     - Use known lattice parameters and space group
     - Build using pymatgen Structure or ASE Atoms

2. **Generate surface using SlabGenerator**
   - Use pymatgen SlabGenerator or equivalent tool
   - Specify Miller indices for surface orientation
   - Set number of layers (typically 4-8 for adequate thickness)
   - Set vacuum thickness (typically 10-15 Å)

3. **Validate surface structure**
   - Verify correct Miller indices and surface orientation
   - Check surface termination (some materials have multiple terminations)
   - Ensure proper coordination of surface atoms
   - Verify PBC settings: (T, T, F) for surface calculations

4. **Save and document**
   - Save in multiple formats (CIF, XYZ, POSCAR)
   - Document Materials Project ID if applicable
   - Record surface orientation, number of layers, vacuum thickness

## Key Considerations

### Miller Indices and Surface Stability
- BCC metals: (100), (110), (111) surfaces commonly used
  - BCC (100): typically stable, 4-fold symmetry
  - BCC (110): most dense, often most stable
- FCC metals: (111) often most stable, (100) common
- Perovskites: (001) most common, multiple terminations possible

### Lattice Parameters for Common Materials
| Material | Structure | Lattice Constant (Å) | Space Group |
|----------|-----------|---------------------|--------------|
| Fe | BCC | 2.866 | Im-3m (229) |
| Cu | FCC | 3.615 | Fm-3m (225) |
| Pt | FCC | 3.924 | Fm-3m (225) |

### Layer Count and Vacuum Thickness
- **Layers**: 4-8 layers balance accuracy vs. computational cost
- **Vacuum**: 10-15 Å minimum to prevent periodic image interactions
- **Example**: Fe(100) with 5 layers + 15 Å vacuum gives 10-atom slab

## Common Pitfalls and Fixes

1. **Materials Project API connection failure**
   - Symptom: Cannot download structure from MP
   - Fix: Create structure manually using known parameters
   - Example: BCC Fe with a=2.866 Å, space group Im-3m
   
2. **Primitive vs. conventional cell issues**
   - Symptom: Unexpected atom count in unit cell
   - Fix: Use conventional cell for surface creation
   - BCC primitive: 1 atom; conventional: 2 atoms
   - Use crystal_builder with --cubic true for conventional cells

3. **Incorrect surface termination**
   - Symptom: Wrong surface chemistry
   - Fix: Check termination for polar surfaces (e.g., SrTiO3 (001) has TiO2 or SrO terminations)

4. **Insufficient vacuum thickness**
   - Symptom: Periodic images interacting across vacuum
   - Fix: Increase vacuum to >10 Å minimum

## Additional Tips

- **Reproducibility**: Always document Materials Project ID (e.g., mp-13 for BCC Fe)
- **File formats**: CIF for visualization, XYZ for quick inspection, POSCAR for VASP
- **Surface reconstruction**: Real surfaces may reconstruct; consider relaxation calculations
- **Unsupported structures**: Build manually using scaled_positions (see previous examples for perovskites)
- **File format compatibility**: Some tools prefer CIF format; use ASE for format conversion
- When combining surfaces for interfaces, create both surfaces with similar parameters first
