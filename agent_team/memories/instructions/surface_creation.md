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
   - Set number of layers (typically 4-8 for adequate thickness, 5 for DFT optimization)
   - Set vacuum thickness (typically 10-15 Å minimum)

3. **Build supercell for desired coverage**
   - Expand surface unit cell to accommodate adsorbates
   - Ensure periodic images > 10 Å apart for adsorbates
   - Balance atom count vs. computational cost

4. **Validate surface structure**
   - Verify correct Miller indices and surface orientation
   - Check surface termination (some materials have multiple terminations)
   - Ensure proper coordination of surface atoms
   - Verify PBC settings: (T, T, F) for surface calculations

5. **Save and document**
   - Save in multiple formats (.extxyz preferred, CIF, POSCAR)
   - Document Materials Project ID if applicable
   - Record surface orientation, number of layers, vacuum thickness

## Key Considerations

### Miller Indices and Surface Stability
- BCC metals: (100), (110), (111) surfaces commonly used
  - BCC (100): typically stable, 4-fold symmetry
  - BCC (110): most dense, often most stable
- FCC metals: (111) often most stable, (100) common
- Perovskites: (001) most common, multiple terminations possible
- Oxides: (001), (100), (101), (110) orientations common

### SiO2 (α-Quartz) Surface Example
- Source: mp-6930 (α-quartz, trigonal P3_221)
- Common orientations: (001), (100), (101), (110)
- Layer optimization: 5 layers sufficient for DFT (reduced from 8)
- Supercell sizing: maintain > 10 Å periodic image distance for adsorbates

| Surface | Typical Supercell | Dimensions (Å) | Layers | Atoms (5 layers) |
|---------|-------------------|----------------|--------|------------------|
| SiO2 (001) | 4×4×1 | 19.7×19.7 | 5 | 405 |
| SiO2 (100) | 4×3×1 | 19.7×16.3 | 5 | 417 |
| SiO2 (101) | 3×4×1 | 22.0×19.7 | 5 | 270 |
| SiO2 (110) | 2×3×1 | 17.0×16.3 | 5 | 282 |

### Lattice Parameters for Common Materials
| Material | Structure | Lattice Constant (Å) | Space Group |
|----------|-----------|---------------------|-------------|
| Fe | BCC | 2.866 | Im-3m (229) |
| Cu | FCC | 3.615 | Fm-3m (225) |
| Pt | FCC | 3.924 | Fm-3m (225) |
| SiO2 (α-quartz) | Trigonal | a=4.91, c=5.40 | P3_221 (154) |

### Layer Count and Vacuum Thickness
- **Layers**: 4-8 layers balance accuracy vs. computational cost
- **For DFT optimization**: 5 layers often sufficient
- **Vacuum**: 10-15 Å minimum to prevent periodic image interactions
- **Example**: Fe(100) with 5 layers + 15 Å vacuum gives 10-atom slab

## Common Pitfalls and Fixes

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| MP API connection failure | Cannot download structure | Create manually using known parameters |
| Primitive vs. conventional cell | Unexpected atom count | Use conventional cell for surface creation |
| Incorrect surface termination | Wrong surface chemistry | Check termination for polar surfaces |
| Insufficient vacuum thickness | Periodic images interacting | Increase vacuum to >10 Å minimum |
| Too many layers for DFT | Excessive computational cost | Reduce to 5 layers, verify surface properties |
| Wrong supercell size | Adsorbate periodic images < 10 Å | Calculate based on adsorbate size |

### Layer Optimization
- Initial structures may use 8 layers for surface stability
- For DFT, reduce to 5 layers to minimize computational cost
- Example: SiO2 (001) 8 layers → 5 layers: 1152 atoms → 405 atoms (65% reduction)
- Always verify surface properties maintained with fewer layers

## Additional Tips

### Supercell Sizing Strategy
1. Calculate adsorbate maximum dimension
2. Double the adsorbate size to get minimum supercell dimension
3. Check surface unit cell dimensions
4. Choose supercell expansion that gives > 10 Å between periodic images
5. Verify after construction

### File Format Recommendations
- **.extxyz**: Preferred - preserves all structural info including PBC
- **CIF**: For visualization and compatibility
- **POSCAR**: For VASP calculations
- Use ASE for format conversion: `ase build --change-format <format>`

### Surface Reconstruction
- Real surfaces may reconstruct; consider relaxation calculations
- Clean surfaces may have different stable terminations
- Check literature for known surface reconstructions

### Reproducibility
- Always document Materials Project ID (e.g., mp-6930 for α-quartz)
- Record surface orientation, number of layers, vacuum thickness
- Note supercell expansion used

### When Combining Surfaces for Interfaces
- Create both surfaces with similar parameters first
- Use build_interface tool for lattice matching (see interface_building.md)

### Validation Checklist
- [ ] Correct Miller indices and surface orientation
- [ ] Proper surface termination
- [ ] Sufficient layers (5+ for DFT)
- [ ] Sufficient vacuum (> 10 Å)
- [ ] Supercell size appropriate for intended use
- [ ] PBC settings correct (T, T, F)
- [ ] Documentation includes MP ID, orientation, layers, vacuum
