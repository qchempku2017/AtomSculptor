# Materials Project Search Instructions

## Common Workflow

1. **Identify target material properties**
   - Determine chemical composition (e.g., SiO2)
   - Specify crystal structure or polymorph if known (e.g., hexagonal, β-quartz)
   - Note any specific requirements (space group, stability)

2. **Search Materials Project database**
   - Use composition-based search
   - Filter by relevant criteria (energy above hull, space group)
   - Review candidate structures

3. **Select appropriate structure**
   - Check Materials Project ID (mp-XXXXX)
   - Verify crystal structure matches requirements
   - Note space group and lattice parameters

4. **Download and import structure**
   - Use appropriate tools to fetch structure from Materials Project
   - Verify imported structure integrity

## Key Considerations

- **Polymorph selection**: Many materials have multiple polymorphs
  - Example: SiO2 has multiple forms (quartz, cristobalite, tridymite)
  - β-quartz (mp-6922) with space group P6222 is a common hexagonal form
- **Stability**: Check "energy above hull" to assess thermodynamic stability
- **Lattice matching**: When using for interfaces, consider lattice parameters relative to other materials

## Common Pitfalls and Fixes

1. **Non-existent crystal structure**: Searching for a structure that doesn't exist in nature
   - Example: Searching for "hcp SiO2" - true hcp SiO2 doesn't exist
   - Fix: Use closest polymorph that meets requirements (e.g., hexagonal β-quartz)

2. **Multiple candidates**: Many structures match search criteria
   - Fix: Use additional filters (space group, formation energy, band gap) to narrow down

## Additional Tips

- Always note the Materials Project ID for reproducibility
- Space group can help quickly identify polymorphs
- Cross-reference with literature for commonly used structures
- Some structures may require primitive cell conversion before use
