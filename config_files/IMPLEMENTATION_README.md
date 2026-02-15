# Boundary Condition and Load Customization Implementation

## Implementation Summary

This implementation adds support for structure-type-specific boundary conditions and loads configuration to the ANSYS Automation system. The enhancement allows different structure types to have different combinations of constraints and loading patterns without requiring code modifications.

## What Was Implemented

### 1. Configuration Files

Created structure-specific configuration files for existing structure types:

- **structure_151_config.json**: Configuration for structure type 151
  - Boundary Conditions: Fixed Support + Rotation Constraint
  - Loads: Force (from database) + Bolt Pretension

- **structure_131_132_config.json**: Configuration for structure type 131/132
  - Boundary Conditions: Fixed Support + Rotation Constraint
  - Loads: Force (from database) + Bolt Pretension

- **structure_2045_config.json**: Example configuration for structure type 2045
  - Boundary Conditions: Fixed Support + Frictionless Support
  - Loads: Force + Moment (both from database)

### 2. Enhanced AnalysisManager

Enhanced the `AnalysisManager` class with the following capabilities:

#### New Methods

- `validate_configuration()`: Validates boundary conditions and loads configuration
- `_validate_boundary_conditions_config()`: Validates BC configuration completeness
- `_validate_loads_config()`: Validates loads configuration completeness
- `_apply_boundary_conditions_from_config()`: Applies BCs from structure-specific config
- `_apply_boundary_conditions_legacy()`: Maintains backward compatibility with old config
- `_apply_loads_from_config()`: Applies loads from structure-specific config
- `_apply_loads_legacy()`: Maintains backward compatibility with old config
- `get_validation_errors()`: Returns list of validation errors
- `clear_validation_errors()`: Clears validation errors list

#### Boundary Condition Application Methods

- `_apply_fixed_support()`: Apply fixed support BC
- `_apply_rotation_constraint()`: Apply rotation constraint (Remote Displacement with RotX=RotY=RotZ=0)
- `_apply_displacement()`: Apply displacement BC with components
- `_apply_remote_displacement()`: Apply remote displacement with custom components
- `_apply_frictionless_support()`: Apply frictionless support BC
- `_apply_compression_only_support()`: Apply compression-only support BC

#### Load Application Methods

- `_apply_force_load()`: Apply force load with X, Y, Z components (database or static)
- `_apply_moment_load()`: Apply moment load (database or static)
- `_apply_pressure_load()`: Apply pressure load (database or static)
- `_apply_remote_force_load()`: Apply remote force load
- `_apply_bearing_load()`: Apply bearing load
- `_apply_temperature_load()`: Apply temperature load

### 3. Configuration Schema

Defined two new configuration sections:

#### boundary_conditions_config

List of boundary condition definitions with:
- `type`: Boundary condition type
- `named_selection`: Named selection to apply BC to
- `components`: Optional parameters for displacement/rotation (type-specific)

#### loads_config

List of load definitions with:
- `type`: Load type
- `named_selection`: Named selection to apply load to
- `use_database`: Boolean flag to use load_database.json values
- `components`: Optional static values (fx, fy, fz for force; mx, my, mz for moment)
- `value`: Optional static value for pressure/temperature

## Supported Types

### Boundary Condition Types

1. **fixed_support**: Fully constrained support
2. **rotation_constraint**: Rotation prohibition (RotX=RotY=RotZ=0)
3. **displacement**: Prescribed displacement with components
4. **remote_displacement**: Remote displacement with custom components
5. **frictionless_support**: Frictionless constraint
6. **compression_only_support**: Compression-only contact

### Load Types

1. **force**: Direct force with X, Y, Z components
2. **moment**: Direct moment application
3. **pressure**: Pressure load
4. **remote_force**: Remote point force
5. **bearing_load**: Bearing load
6. **bolt_pretension**: Bolt pretension (automatic)
7. **temperature**: Temperature load

## Key Features

### 1. Backward Compatibility

The implementation maintains full backward compatibility:
- If no structure-specific configuration exists, uses base project_settings.json
- If structure config exists without new sections, falls back to base configuration
- Existing configurations continue to work unchanged

### 2. Validation

Comprehensive validation includes:
- Type validation (supported types)
- Named selection existence checks
- Parameter completeness validation
- Database reference validation
- Detailed error and warning messages

### 3. Extensibility

New structure types can be added by:
1. Creating a new configuration file: `structure_{type}_config.json`
2. Defining boundary conditions and loads
3. No code changes required

### 4. Flexibility

Supports both database-driven and static values:
- **Database-driven** (`use_database: true`): Values from load_database.json
- **Static values** (`use_database: false`): Values specified in configuration

## Analysis Scenarios Format (`analysis_scenarios.json`)

`load_factors` are now sourced only from `analysis_scenarios` and used uniformly for both load-application branches (legacy + structure-specific `loads_config`).

Required fields per scenario:
- `steps` (int)
- `load_factors` (list[float])

Validation rules:
- `len(load_factors) == steps`.
- If `has_bolts=True`, solver timeline uses one additional zero step: `time_steps = steps + 1`, `load_factors_shifted = [0] + load_factors`.
- Shifted factors length must match generated `time_steps` length.

Execution load configuration (`ExecutionManager.get_load_configuration`) contains only force/moment (and optional pressure) values from the load database; scenario factors are not duplicated there.

## Usage Examples

### Applying Boundary Conditions and Loads

```python
# The system automatically detects and uses structure-specific configuration
analysis_manager.apply_boundary_conditions(analysis)
analysis_manager.apply_loads(analysis, load_config, scenario_name, has_bolts)
```

### Validating Configuration

```python
# Validate before applying
validation = analysis_manager.validate_configuration()

if validation["is_valid"]:
    print("Configuration is valid")
else:
    print("Errors found:")
    for error in validation["errors"]:
        print(f"  - {error}")
    
    print("Warnings:")
    for warning in validation["warnings"]:
        print(f"  - {warning}")
```

### Checking Validation Errors After Application

```python
# After applying boundary conditions and loads
errors = analysis_manager.get_validation_errors()
if errors:
    print("Issues encountered during application:")
    for error in errors:
        print(f"  - {error}")
```

## File Structure

```
config_files/
├── structure_151_config.json              # Configuration for type 151
├── structure_131_132_config.json          # Configuration for type 131/132
├── structure_2045_config.json             # Example for type 2045
├── BOUNDARY_CONDITIONS_LOADS_CONFIG_GUIDE.md  # User guide
└── [other existing config files]

managers/
└── analysis_manager.py                    # Enhanced AnalysisManager
```

## Testing Recommendations

1. **Test with existing structure types (151, 131/132)**
   - Verify boundary conditions are applied correctly
   - Verify loads from database are retrieved and applied
   - Verify bolt pretension is handled by BoltManager

2. **Test backward compatibility**
   - Rename structure config files temporarily
   - Verify system falls back to legacy method
   - Verify no errors occur

3. **Test validation**
   - Test with missing named selections
   - Test with invalid types
   - Test with incomplete parameters
   - Verify validation messages are helpful

4. **Test new structure type (2045)**
   - Create model with appropriate named selections
   - Apply configuration
   - Verify different BC/load combination works

5. **Test static values**
   - Create configuration with `use_database: false`
   - Specify static force/moment/pressure values
   - Verify values are applied correctly

## Integration with Existing System

The implementation integrates seamlessly with existing components:

- **ConfigurationManager**: Automatically loads structure-specific configs
- **NamedSelectionManager**: Used for named selection lookups (no changes needed)
- **BoltManager**: Handles bolt pretension (no changes needed)
- **ExecutionManager**: Calls AnalysisManager methods (no changes needed)

## Migration Guide

### For Existing Projects

1. No changes required - system is backward compatible
2. To use new features:
   - Create structure-specific config file
   - Add `boundary_conditions_config` section
   - Add `loads_config` section
   - Test with validation before deploying

### For New Projects

1. Create structure-specific configuration from the start
2. Use new configuration schema for clearer structure
3. Leverage validation to catch issues early

## Future Enhancements

Potential future improvements:

1. **Configuration Templates**: Provide reusable templates for common patterns
2. **GUI Configuration Editor**: Visual tool for creating configurations
3. **Configuration Inheritance**: Allow configs to inherit from base templates
4. **Enhanced Validation**: More detailed validation rules and suggestions
5. **Load Combination Support**: Support for multiple load cases and combinations

## Documentation

Complete documentation is available in:
- **BOUNDARY_CONDITIONS_LOADS_CONFIG_GUIDE.md**: Comprehensive user guide
- **Code comments**: Inline documentation in analysis_manager.py
- **This README**: Implementation overview and technical details

## Support

For issues or questions:
1. Check validation messages for specific errors
2. Review BOUNDARY_CONDITIONS_LOADS_CONFIG_GUIDE.md for examples
3. Verify named selections exist in the model
4. Check load_database.json for required structure type entries
