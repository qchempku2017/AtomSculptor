# Sandwich Structure Creation Instructions

## Common Workflow

1. **Design sandwich architecture**
   - Identify substrate materials (top and bottom layers)
   - Identify molecule/layer to be sandwiched in the middle
   - Example: Fe | Ibuprofen | SiO2 sandwich structure

2. **Create individual components**
   - Generate or obtain bottom substrate surface (e.g., Fe (100))
   - Generate or obtain top substrate surface (e.g., hexagonal SiO2 (001))
   - Create molecule using SMILES or other method with geometry optimization

3. **Build lattice-matched interface**
   - Use build_interface tool with ZSL algorithm
   - Set gap parameter to accommodate molecule plus margins
   - Example: 15 Å gap for 4.5 Å thick molecule

4. **Check supercell dimensions**
   - Verify molecule fits within lateral cell dimensions
   - Ensure 10-15 Å margin in all lateral directions
   - Expand supercell if necessary

5. **Insert molecule into gap**
   - Place molecule at center of gap region
   - Verify no overlaps with substrate atoms
   - Check molecular orientation is appropriate

## Key Considerations

- **Gap sizing**: Gap must accommodate molecule with room for flexibility
  - Measure optimized molecule dimensions
  - Add margins for molecule movement during simulation
  - Example: 15 Å gap for 4.5 Å thick ibuprofen provides ~10 Å total margin

- **Lattice matching**: Critical for creating defect-free interface
  - Use ZSL algorithm in build_interface tool
  - Different crystal structures (e.g., bcc Fe and hexagonal SiO2) can be matched
  - Some lattice strain may be unavoidable

- **Molecule generation**: Use appropriate method
  - SMILES strings can generate initial 3D structure
  - Geometry optimization (e.g., MMFF with RDKit) provides realistic dimensions
  - Final structure: 391 atoms, ~17×16 Å lateral dimensions

## Common Pitfalls and Fixes

1. **PBC gaps from manual stacking**: Attempting to manually stack surfaces
   - Symptom: Gaps across periodic boundaries
   - Fix: Always use build_interface tool for lattice matching

2. **Cell too small for molecule**: Lateral dimensions insufficient
   - Symptom: Molecule dimension exceeds cell dimension
   - Fix: Build supercell expansion before molecule insertion
   - Example: 4x2 supercell (35.06 × 36.50 Å) for 11.43 Å ibuprofen

3. **Molecule overlaps with substrate**: Gap too small
   - Symptom: Atom positions overlap after insertion
   - Fix: Increase gap parameter and re-insert molecule

## Additional Tips

- Verify molecule is properly centered in the gap region
- Check final atom count matches expectation (substrate + molecule atoms)
- Consider molecule orientation relative to substrate surfaces
- For multiple molecules, ensure sufficient spacing between them
- Document all Materials Project IDs for reproducibility
