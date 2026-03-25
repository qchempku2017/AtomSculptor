# Nanostructure Creation Instructions

## Common Workflow

1. **Determine nanostructure type and geometry**
   - Nanoparticle: faceted shapes (icosahedron, decahedron, octahedron, etc.)
   - Nanoshell: hollow or solid spherical shells
   - Other shapes: rods, cubes, etc.

2. **Select construction method based on structure type**

   **For metallic nanoparticles:**
   - Use ASE's cluster tools or manual construction
   - Specify number of shells or total atoms
   - Common shapes: icosahedron, cuboctahedron, decahedron
   
   **For crystalline nano-shells:**
   - Start from real crystal structure (e.g., from Materials Project)
   - Build large supercell to provide sufficient material
   - Cut desired geometry maintaining crystalline order

3. **Build structure**
   - For nanoparticles: Define shape, element, and size
   - For nanoshells: Build supercell, then cut spherical shell
   - Ensure sufficient atoms for meaningful statistics

4. **Validate nanostructure**
   - Check atomic coordination (especially for surface atoms)
   - Verify bond lengths are realistic
   - For shells: ensure proper thickness and geometry
   - Check surface-to-volume ratio if relevant

5. **Save and document**
   - Export in multiple formats (CIF, XYZ)
   - Document construction parameters
   - Record Materials Project ID if applicable

## Key Considerations

### Nanoparticle Shapes and Sizes
- **Icosahedron**: Common for Pt, Au nanoparticles due to low surface energy
  - 147 atoms = 4 shells (commonly used size)
  - Closed-shell magic numbers: 13, 55, 147, 309, 561, 923, ...
- **Cuboctahedron**: Intermediate between cube and octahedron
- **Decahedron**: Five-fold symmetry, common for FCC metals
- **Size selection**: Balance computational cost vs. realistic size

### Nanoshell Construction from Crystalline Materials
- **Critical**: Use real crystal structure, not random placement
- **Workflow**:
  1. Search Materials Project for stable bulk structure
  2. Build large supercell (e.g., 7×7×7 for 3D structures)
  3. Cut spherical shell from supercell center
  4. Maintain crystalline order and proper bonding
- **Example**: SiO2 alpha-quartz (mp-6930) → 7×7×7 supercell → spherical shell

### Coordination and Bonding
- Surface atoms have reduced coordination
- For oxides (e.g., SiO2): Check Si-O bonds (~1.6 Å for quartz)
- For metals: Check nearest-neighbor distances
- Ensure no unrealistic bond lengths or angles

## Common Pitfalls and Fixes

1. **Random atom placement for crystalline nanostructures**
   - Symptom: Overlapping atoms, unrealistic bonding, coordination errors
   - Cause: Placing atoms randomly without crystal structure consideration
   - Fix: Start from real crystal structure (MP), build supercell, then cut geometry

2. **Insufficient supercell size for shells**
   - Symptom: Shell too small or incomplete
   - Cause: Supercell not large enough to cut desired shell size
   - Fix: Increase supercell expansion (e.g., 5×5×5 → 7×7×7)

3. **Non-magic number nanoparticle size**
   - Symptom: Incomplete shells, high surface energy
   - Cause: Choosing atom count not matching closed-shell structure
   - Fix: Use magic numbers (13, 55, 147, 309, ...) for nanoparticles

4. **Wrong nanoparticle shape for element**
   - Symptom: Unrealistic surface structure
   - Cause: Choosing shape incompatible with element's preferred structure
   - Fix: Consider element-specific preferences (e.g., icosahedra for Pt nanoparticles)

5. **Ignoring surface effects**
   - Symptom: Unexpected surface reconstruction
   - Cause: Not accounting for reduced coordination at surfaces
   - Fix: Allow for surface relaxation in subsequent calculations

## Additional Tips

### Material-Specific Considerations
- **Pt nanoparticles**: Icosahedral shape common, low surface energy
- **SiO2 shells**: Use alpha-quartz (mp-6930) as starting structure
- **Metal oxides**: Check cation-anion coordination carefully

### Magic Numbers for Closed-Shell Clusters
- Icosahedra: 1, 13, 55, 147, 309, 561, 923, 1415, ...
- Cuboctahedra (FCC): Same as icosahedra
- Use these sizes for stable, realistic nanoparticles

### Validation Checklist
- [ ] Bond lengths match expected values
- [ ] Coordination numbers reasonable for surface atoms
- [ ] No overlapping atoms or unrealistic geometries
- [ ] Proper stoichiometry maintained (for compounds)
- [ ] Surface atoms properly terminated (for oxides)

### File Formats
- XYZ: Good for visualization and quick inspection
- CIF: Preserves crystallographic information
- POSCAR: For VASP calculations
- Use ASE for format conversion: `ase build --change-format <format>`
