# Surface Adsorption Instructions

## Common Workflow

1. **Create substrate surface**
   - Generate appropriate surface (see surface_creation.md)
   - Determine supercell size based on adsorbate and periodic image requirements
   - Ensure sufficient vacuum (> 10 Å, more for large adsorbates)

2. **Generate adsorbate molecule**
   - Use ASE `molecule()` function for pre-optimized molecular geometries
   - Alternatively, read from database or construct manually
   - Verify molecular geometry is reasonable

3. **Place adsorbate on surface**
   - Choose adsorption site (top, bridge, hollow, etc.)
   - Set adsorption height (typical distances: 2.2-2.7 Å for O-metal bonds)
   - Orient molecule appropriately for desired adsorption mode

4. **Verify structure integrity**
   - Check all interatomic distances, especially between adsorbate and surface
   - Ensure minimum distance > 2.0 Å to avoid steric clashes
   - Calculate periodic image distances

5. **Save and document**
   - Save structure in appropriate format
   - Document adsorption site, height, and orientation parameters

## Key Considerations

### Supercell Sizing for Adsorbates
- **Critical**: Periodic images of adsorbates must be > 10 Å apart
- Calculate required supercell: account for both adsorbate size and surface unit cell
- Progressively test supercell sizes: 2x2, 3x3, 4x4, 5x5, 6x6
- Verify actual periodic image distances after construction

### Adsorption Parameters
- **Adsorption height**: Depends on adsorbate and surface
  - O-metal: typically 2.2-2.7 Å
  - C-metal: typically 2.0-2.5 Å
  - N-metal: typically 2.0-2.5 Å
  - H-metal: typically 1.5-2.0 Å
- **Orientation**: Match molecular symmetry to surface site symmetry
- **Site selection**: Consider coordination and reactivity

### Periodic Image Distance Checking
- For each atom in adsorbate, find distance to nearest periodic image
- Minimum distance across all atoms should be > 10 Å
- Use ASE or similar tools to calculate these distances
- Larger molecules require larger supercells

## Common Pitfalls and Fixes

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Steric clashes | Pt-adsorbate distances < 2.0 Å | Increase adsorption height; reorient molecule |
| Periodic image interactions | Adsorbate images < 10 Å apart | Increase supercell size (e.g., 2x2 → 3x3 or larger) |
| Incorrect adsorption geometry | Unexpected binding mode | Adjust molecule orientation; check adsorption site |
| Too large supercell | Excessive computational cost | Balance accuracy vs. cost; 10 Å is minimum threshold |

### Supercell Sizing Examples
- **2x2 supercell**: Small adsorbates only
- **3x3 supercell**: May still have < 10 Å for medium adsorbates
- **4x4 supercell**: Often sufficient for medium adsorbates
- **5x5 to 6x6 supercell**: Required for larger molecules (e.g., ethanol)
- **Always verify**: Calculate actual distances, don't assume

## Additional Tips

- Use ASE `molecule()` function for standard organic molecules - provides reasonable starting geometries
- For reactive surfaces, consider multiple adsorption configurations (different sites, orientations)
- After placing adsorbate, always verify:
  1. Minimum adsorbate-surface distance > 2.0 Å
  2. Periodic image distances > 10 Å
  3. Molecular geometry is not severely distorted
- Consider surface relaxation effects - top layer atoms may shift upon adsorption
- For multiple adsorbates, ensure they are sufficiently separated (> minimum interaction distance)
- Document all construction parameters for reproducibility: supercell size, adsorption height, orientation, site type
