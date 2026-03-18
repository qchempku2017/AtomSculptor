# Materials Project API Search Instructions

## Common Workflow

### Basic Material Search
1. Initialize MPRester with your API key:
   ```python
   from mp_api.client import MPRester
   mpr = MPRester("YOUR_API_KEY")
   ```

2. Use `search()` method with appropriate filters (NOT `_search()` for most cases):
   ```python
   results = mpr.materials.summary.search(
       elements=["Fe", "Si", "O"],           # Required elements
       num_elements=(3, 3),                   # Element count range (min, max)
       energy_above_hull=(0, 0.05),           # Stability range in eV/atom
       fields=["material_id", "formula_pretty", "energy_above_hull", "nelements"]
   )
   ```

3. Sort results client-side if needed:
   ```python
   results_list = list(results)
   results_list.sort(key=lambda x: x.nelements, reverse=True)
   ```

4. Convert Element objects to strings when displaying:
   ```python
   elements_str = ', '.join([str(e) for e in sorted(doc.elements)])
   # or use: e.symbol for just the symbol
   ```

### Finding Materials with Most Elements
1. Use reasonable lower bound with `num_elements`:
   ```python
   results = mpr.materials.summary.search(
       num_elements=(5, None),  # Materials with 5+ elements
       fields=["material_id", "formula_pretty", "nelements", "elements"]
   )
   ```

2. Sort client-side to find maximum:
   ```python
   results_list = list(results)
   results_list.sort(key=lambda x: x.nelements, reverse=True)
   max_elements = results_list[0].nelements
   ```

### Downloading Crystal Structures
1. Retrieve structure by material ID:
   ```python
   structure = mpr.get_structure_by_material_id("mp-20313")
   ```

2. Save structure to file:
   ```python
   structure.to(filename="material.cif")  # CIF format
   # or
   structure.to(filename="POSCAR")        # POSCAR format
   ```

## Key Considerations

### API Method Selection
- Use `search()` for standard queries with common filters
- Use `_search()` only when you need advanced features like sorting on server-side (may have compatibility issues)
- Server-side sorting parameters (`sort_fields`, `ascending`, `size`) are NOT supported in `search()` method

### Database Limitations
- Materials Project database maximum element count is **9 elements** (as of current data)
- Not all theoretical compounds exist in the database
- Use reasonable element count ranges (e.g., `num_elements=(3, 3)` for ternaries)

### Element Handling
- The `elements` field returns `pymatgen.Element` objects, NOT strings
- Always convert Element objects using `str(e)` or `e.symbol` for display
- Element lists can be sorted for consistent output

### Stability Criteria
- Use `energy_above_hull` to find stable compounds:
  - `(0, 0)` for compounds on the convex hull
  - `(0, 0.05)` for near-stable compounds within 50 meV/atom
- Lower values indicate higher stability

## Common Pitfalls and Fixes

### Pitfall 1: Invalid kwargs in search()
**Problem**: Using `sort_fields`, `ascending`, `size` in `search()` method
**Error**: "You have specified the following kwargs which are unknown to `search`, but may be known to `_search`"
**Fix**: Remove these parameters from `search()` and sort results client-side instead

### Pitfall 2: Server rejection with sort parameter
**Problem**: Using `_search()` with `sort="-nelements"` 
**Error**: "The server does not support the request made..."
**Fix**: Avoid server-side sorting; fetch data and sort client-side with Python

### Pitfall 3: Empty results for high element counts
**Problem**: Query with `num_elements=(10, None)` returns 0 results
**Fix**: Use reasonable lower bounds (e.g., `(5, None)`) and check database limits (max 9 elements)

### Pitfall 4: TypeError with Element objects
**Problem**: Printing elements directly: `print(d.elements)`
**Error**: "TypeError: sequence item 0: expected str instance, Element found"
**Fix**: Convert to strings: `', '.join([str(e) for e in sorted(d.elements)])` or `[e.symbol for e in d.elements]`

## Additional Tips

### Efficient Query Strategy
- Always specify `fields` parameter to reduce data transfer and improve speed
- Common useful fields: `material_id`, `formula_pretty`, `energy_above_hull`, `nelements`, `elements`, `structure`
- Use `num_elements` as tuple `(min, max)` or single value for exact count

### Result Processing
- `search()` returns a generator; convert to list for multiple iterations: `results_list = list(results)`
- Use `formula_pretty` for human-readable formulas (e.g., "Fe2SiO4" instead of "Fe2Si1O4")
- Material IDs follow format: "mp-XXXXXX"

### Documentation Resources
- Official API docs: https://materialsproject.github.io/api/
- Check for package updates if encountering server errors
- Use `help(mpr.materials.summary.search)` for available parameters

### Example Search Patterns

**Find stable binary compounds:**
```python
mpr.materials.summary.search(
    elements=["Fe", "O"],
    num_elements=(2, 2),
    energy_above_hull=(0, 0.05)
)
```

**Find ternary compounds with specific element:**
```python
mpr.materials.summary.search(
    elements=["Fe"],  # Must contain Fe
    num_elements=(3, 3),
    energy_above_hull=(0, 0)
)
```

**Find most complex compounds:**
```python
mpr.materials.summary.search(
    num_elements=(7, None),
    fields=["material_id", "formula_pretty", "nelements"]
)
```
