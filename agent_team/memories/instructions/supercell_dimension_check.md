# Supercell Dimension Check Instructions

## Common Workflow

1. **Measure molecule dimensions**
   - Calculate the maximum extent of the molecule in all directions
   - For flexible molecules, consider optimized geometry
   - Example: Ibuprofen optimized with MMFF has dimensions ~11.43 × 4.5 Å

2. **Check supercell lateral dimensions**
   - Compare molecule dimensions with supercell a, b parameters
   - Calculate available margin: (cell_dimension - molecule_dimension) / 2

3. **Verify minimum margin requirements**
   - For molecular simulations: require at least 10-15 Å margin
   - This prevents periodic image interactions
   - Example: If molecule is 11.43 Å, cell must be >21 Å in that direction

4. **Expand supercell if necessary**
   - If margins insufficient, build supercell expansion
   - Example: 4x2 supercell expansion created 35.06 × 36.50 Å cell
   - Re-verify margins after expansion

## Key Considerations

- **Periodic image interactions**: Molecules interacting with their images across PBC
  - Minimum 10-15 Å gap needed between molecule and its periodic images
  - This translates to 10-15 Å margin from molecule edge to cell boundary
- **Molecular geometry**: Use relaxed/optimized geometry for dimension calculations
  - SMILES-derived structures should be geometry-optimized (e.g., with MMFF)
- **Supercell expansion factor**: Choose to provide adequate margins in all directions
  - May need asymmetric expansion (e.g., 4x2) depending on cell shape

## Common Pitfalls and Fixes

1. **Molecule exceeds cell dimension**: Molecule larger than cell in one direction
   - Symptom: Molecule dimension > cell dimension
   - Fix: Build supercell expansion before inserting molecule
   - Example: Initial cell 8.77 Å too small for 11.43 Å ibuprofen

2. **Insufficient margin for periodic images**: Margins < 10 Å
   - Symptom: Molecule too close to periodic boundaries
   - Fix: Expand supercell to provide adequate buffer zone

3. **Not accounting for all molecular orientations**: Only checking one dimension
   - Fix: Check all lateral dimensions (x, y) for sufficient margin

## Additional Tips

- Always verify dimensions BEFORE inserting molecules
- Use molecular visualization to check positioning
- For large molecules, larger supercells may be necessary despite computational cost
- Consider molecule flexibility - may need extra margin for conformational changes
- When in doubt, err on the side of larger supercells for safety
