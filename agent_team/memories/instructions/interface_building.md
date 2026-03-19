# Interface Building Instructions

## Common Workflow

1. **Prepare individual surfaces**
   - Create or obtain both surface structures separately
   - Ensure surface orientations are appropriate for interface
   - Verify both structures have adequate vacuum layers

2. **Use build_interface tool for lattice matching**
   - Apply ZSL (Zur狗 Super Lattice) algorithm for automatic lattice matching
   - Specify both surface structures and their orientations
   - Set appropriate gap distance for interface region

3. **Configure interface parameters**
   - Set gap distance based on intended use:
     - For simple interfaces: typical gap ~2-3 Å
     - For molecular insertion: gap should accommodate molecule plus margins
     - Example: 15 Å gap for 4.5 Å thick ibuprofen molecule
   - Specify maximum strain tolerance for lattice matching

4. **Verify interface quality**
   - Check for gaps across periodic boundaries
   - Verify lattice strain is acceptable
   - Ensure interface atoms have reasonable coordination

## Key Considerations

- **Lattice matching algorithm**: ZSL automatically finds matching supercells
  - Example: Fe (100) surface matched with hexagonal SiO2 (001) surface
  - Resulted in 8.77 × 17.71 Å interface cell
- **Gap sizing**: Critical for molecular simulations
  - Must accommodate molecule dimensions
  - Consider molecule orientation and flexibility
- **PBC consistency**: Interface tool handles periodic boundary conditions automatically
  - No manual stacking - always use build_interface for lattice-matched interfaces

## Common Pitfalls and Fixes

1. **PBC gaps from manual stacking**: Attempting to manually stack surfaces with mismatched lattices
   - Symptom: Gaps across periodic boundaries
   - Fix: Use build_interface tool with ZSL algorithm instead of manual stacking

2. **Insufficient gap for molecules**: Gap too small for intended molecular layer
   - Symptom: Molecule overlaps with substrate
   - Fix: Increase gap parameter to accommodate molecule plus margins

3. **Excessive lattice strain**: Matched lattices have high strain
   - Fix: Adjust maximum strain tolerance or try different surface orientations

## Additional Tips

- Always check final cell dimensions after interface creation
- For molecular systems, plan gap size based on largest molecular dimension
- Lattice matching may create non-square supercells - this is normal
- Interface quality significantly impacts downstream simulation accuracy
