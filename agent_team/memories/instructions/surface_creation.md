# Surface Creation Instructions

## Common Workflow

1. **Identify crystal structure and surface orientation**
   - Determine bulk crystal structure (e.g., bcc, fcc, hcp)
   - Choose surface Miller indices (e.g., (100), (111), (001))
   - Obtain lattice constant for the material

2. **Create surface using appropriate tool**
   - Use surface creation tool with bulk parameters
   - Specify number of layers (typically 4-8 layers for adequate thickness)
   - Set vacuum layer (typically 10-15 Å for surface studies)

3. **Validate surface structure**
   - Check that surface atoms have proper coordination
   - Verify cell dimensions and periodicity
   - Ensure surface is not interacting with its periodic images

## Key Considerations

- **Lattice constants**: Use experimentally verified values when possible
  - Example: bcc Fe lattice constant = 2.87 Å
- **Layer count**: Balance between computational cost and surface model accuracy
  - Too few layers: bulk-like behavior not captured
  - Too many layers: unnecessary computational expense
- **Vacuum thickness**: Must be sufficient to prevent periodic image interactions (typically >10 Å)
- **Surface termination**: Some materials have multiple possible terminations; choose based on stability

## Common Pitfalls and Fixes

1. **PBC gaps across boundaries**: When combining with other surfaces or substrates
   - Fix: Ensure lattice matching before combining surfaces (see interface_building.md)
   
2. **Incorrect surface orientation**: Miller indices don't match desired surface
   - Fix: Double-check surface normal vector and Miller index convention

## Additional Tips

- For bcc structures, (100) surfaces are often stable and commonly used
- Surface reconstruction may occur in real systems but typically requires relaxation calculations
- When creating surfaces for interface studies, consider the matching requirements with the second material
