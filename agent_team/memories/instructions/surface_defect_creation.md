# Defect Creation Instructions

## Common Workflow

1. **Prepare base structure**
   - Start with pristine crystal or surface structure
   - For surfaces, create using surface creation workflow (see surface_creation.md)
   - Ensure structure has sufficient size for defect concentration desired
   - Convert to CIF format if using defect_builder (extxyz not directly supported)

2. **Select defect type and parameters**
   - **Vacancy**: Remove atom(s) from lattice sites
   - **Substitution**: Replace atom(s) with different element(s)
   - **Interstitial**: Insert atom(s) at non-lattice sites
   - **Antisite**: Swap positions of two different atom types
   - **Defect complex**: Multiple defects in combination

3. **Choose targeting method**
   - **Element-specific**: Target all atoms of a specific element
   - **Coordinate-based**: Target specific positions (for interstitials)
   - **Random**: Statistical distribution across structure
   - **Manual**: Specify exact atom indices

4. **Execute defect creation**
   - Use defect_builder tool with appropriate parameters
   - For reproducibility, set random seed (--seed parameter)
   - Validate concentration matches expectation

5. **Validate defective structure**
   - Check correct number of atoms removed/added
   - Verify atomic distances (no overlapping atoms)
   - Check coordination of atoms near defect sites
   - Ensure minimum distances between defects for multiple defects

## Key Considerations

### Defect Concentration and Supercell Size
- Need sufficient atoms to achieve desired concentration
- Example: 25% vacancy requires at least 16 atoms to get exactly 4 vacancies
- Use supercell expansion to increase atom count if needed
- Balance between defect concentration and computational cost

### Defect Types and Parameters

| Defect Type | Required Parameters | Optional Parameters |
|-------------|-------------------|-------------------|
| Vacancy | Element to remove | Concentration, seed |
| Substitution | Host element, substitution element | Concentration, seed |
| Interstitial | Element to insert, position | Position type (Voronoi), distance constraints |
| Antisite | Two elements to swap | Concentration, seed |
| Complex | JSON file with defect specification | - |

### Interstitial Site Selection
- **Voronoi method**: Automatically finds interstitial sites using Voronoi analysis
- **Coordinate-based**: Specify fractional or Cartesian coordinates manually
- **Distance constraints**:
  - Minimum distance to existing atoms (default 2.0 Å)
  - Minimum distance between interstitials (default 2.5 Å)
- **Important**: Without constraints, interstitials may cluster unrealistically

### File Format Compatibility
- defect_builder.py works with CIF format
- Use ASE to convert between formats (XYZ, POSCAR, CIF)
- Example: `ase build --change-format cif input.xyz output.cif`

## Common Pitfalls and Fixes

1. **Interstitial clustering**
   - Symptom: Interstitials too close together (e.g., < 2 Å apart)
   - Cause: Random distribution without distance constraints
   - Fix: Use --min-dist-to-atoms and --min-dist-between parameters
   - Example: Old method gave interstitials 1.26 Å apart; new method with constraints gives 8-12 Å apart

2. **Wrong file format**
   - Symptom: defect_builder fails to read structure
   - Cause: Using extxyz or other unsupported format
   - Fix: Convert to CIF before running defect_builder

3. **Insufficient atoms for target concentration**
   - Symptom: Cannot achieve exact defect number
   - Cause: Unit cell too small
   - Fix: Build supercell first, then introduce defects

4. **Overlapping atoms**
   - Symptom: Atoms too close after defect insertion
   - Cause: Interstitial placed too close to existing atom
   - Fix: Increase --min-dist-to-atoms parameter

5. **Non-reproducible results**
   - Symptom: Different defect distributions each run
   - Cause: Random placement without seed
   - Fix: Use --seed parameter for reproducibility (e.g., --seed 42)

## Additional Tips

- **Reproducibility**: Always set random seed for reproducible defect distributions
- **Validation**: Check interatomic distances after defect creation
  - Vacancies: Check coordination of neighboring atoms
  - Interstitials: Verify > 2 Å from nearest atoms
  - Substitutions: Check if substitution radius is compatible with site
- **Concentration calculation**: For X% vacancies, need at least 100/X atoms for statistical validity
- **Documentation**: Record all defect parameters (type, concentration, seed) for reproducibility
- **Complex defects**: Use JSON specification file for defect complexes
- **Multiple defect types**: Can be introduced sequentially by running defect_builder multiple times
