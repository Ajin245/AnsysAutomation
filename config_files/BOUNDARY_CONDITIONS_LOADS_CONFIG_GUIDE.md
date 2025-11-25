# Boundary Conditions and Loads Configuration Guide

## Overview

The ANSYS Automation system supports structure-type-specific configuration of boundary conditions and loads. This allows different structure types to have different combinations of constraints and loading patterns without code modifications.

## Configuration Files

Structure-specific configuration files are stored in the `config_files` directory with the naming pattern:
```
structure_{type}_config.json
```

For example:
- `structure_151_config.json` - Configuration for structure type 151
- `structure_131_132_config.json` - Configuration for structure type 131/132

## Configuration Schema

### Boundary Conditions Configuration

The `boundary_conditions_config` section is a list of boundary condition definitions:

```json
{
  "boundary_conditions_config": [
    {
      "type": "boundary_condition_type",
      "named_selection": "ns_name",
      "components": { ... }  // Optional, type-specific
    }
  ]
}
```

### Supported Boundary Condition Types

| Type | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `fixed_support` | Fully constrained support | `named_selection` | - |
| `rotation_constraint` | Rotation prohibition (Remote Displacement with RotX=RotY=RotZ=0) | `named_selection` | - |
| `displacement` | Prescribed displacement | `named_selection` | `components` (x, y, z) |
| `remote_displacement` | Remote point displacement with rotations | `named_selection` | `components` (x, y, z, rotx, roty, rotz) |
| `frictionless_support` | Frictionless constraint | `named_selection` | - |
| `compression_only_support` | Compression-only contact | `named_selection` | - |

### Loads Configuration

The `loads_config` section is a list of load definitions:

```json
{
  "loads_config": [
    {
      "type": "load_type",
      "named_selection": "ns_name",
      "use_database": true,
      "components": { ... },  // Optional, for static values
      "value": 100           // Optional, for static values
    }
  ]
}
```

### Supported Load Types

| Type | Description | Required Parameters | Optional Parameters |
|------|-------------|---------------------|---------------------|
| `force` | Direct force with X, Y, Z components | `named_selection`, `use_database` | `components` (fx, fy, fz) if not using database |
| `moment` | Direct moment application | `named_selection`, `use_database` | `components` (mx, my, mz) if not using database |
| `pressure` | Pressure load | `named_selection`, `use_database` | `value` if not using database |
| `remote_force` | Remote point force | `named_selection` | - |
| `bearing_load` | Bearing load | `named_selection` | - |
| `bolt_pretension` | Bolt pretension from bolt database | - | `automatic: true` |
| `temperature` | Temperature load | `named_selection` | `value` |

## Usage Examples

### Example 1: Structure Type 151

Structure with fixed support, rotation constraints, force from database, and bolt pretension:

```json
{
  "description": "Structure type 151 configuration",
  "boundary_conditions_config": [
    {
      "type": "fixed_support",
      "named_selection": "gu_fixed"
    },
    {
      "type": "rotation_constraint",
      "named_selection": "gu_remote_disp"
    }
  ],
  "loads_config": [
    {
      "type": "force",
      "named_selection": "gu_force",
      "use_database": true
    },
    {
      "type": "bolt_pretension",
      "automatic": true
    }
  ]
}
```

### Example 2: Custom Structure with Static Values

Structure with displacement, custom moment, and pressure:

```json
{
  "description": "Custom structure configuration",
  "boundary_conditions_config": [
    {
      "type": "displacement",
      "named_selection": "gu_support",
      "components": {
        "x": 0,
        "y": 0,
        "z": 0
      }
    }
  ],
  "loads_config": [
    {
      "type": "moment",
      "named_selection": "gu_moment",
      "use_database": false,
      "components": {
        "mx": 0,
        "my": 50000,
        "mz": 0
      }
    },
    {
      "type": "pressure",
      "named_selection": "gu_pressure",
      "use_database": false,
      "value": 10
    }
  ]
}
```

### Example 3: Advanced Remote Displacement

Structure with custom remote displacement allowing specific rotations:

```json
{
  "boundary_conditions_config": [
    {
      "type": "remote_displacement",
      "named_selection": "gu_remote",
      "components": {
        "x": 0,
        "y": 0,
        "z": 0,
        "rotx": 0,
        "roty": 0,
        "rotz": 5
      }
    }
  ]
}
```

## Database-Driven vs Static Values

### Using Database Values (`use_database: true`)

When `use_database` is set to `true`, load values are retrieved from `load_database.json` based on:
- Structure type
- Execution parameters (from model name parsing)

For forces, this includes all three components (fx, fy, fz) as defined in the database.

Example load_database.json structure:
```json
{
  "151": {
    "02": {
      "F1": {
        "nominal_forces": {"fx": 100, "fy": 250, "fz": 500},
        "nominal_moments": {"mx": 0, "my": 15000, "mz": 0}
      }
    }
  }
}
```

### Using Static Values (`use_database: false`)

When `use_database` is `false`, specify load values directly in the configuration:

```json
{
  "type": "force",
  "named_selection": "gu_force",
  "use_database": false,
  "components": {
    "fx": 1000,
    "fy": 2000,
    "fz": 3000
  }
}
```

## Validation

The system validates configurations before application:

### Validation Checks

1. **Type Validation**: Ensures all boundary condition and load types are supported
2. **Named Selection Existence**: Verifies that all referenced named selections exist in the model
3. **Parameter Completeness**: Checks that all required parameters are specified
4. **Database Reference Validity**: For database-driven loads, validates references exist

### Using Validation

```python
# In your analysis setup
validation_results = analysis_manager.validate_configuration()

if not validation_results["is_valid"]:
    print("Configuration errors:")
    for error in validation_results["errors"]:
        print(f"  - {error}")
    
    print("Configuration warnings:")
    for warning in validation_results["warnings"]:
        print(f"  - {warning}")
```

## Backwards Compatibility

The system maintains full backwards compatibility:

1. If no structure-specific configuration exists, the system uses base `project_settings.json`
2. If structure-specific configuration exists but doesn't include `boundary_conditions_config` or `loads_config`, the system falls back to base configuration sections
3. Existing configurations without these new sections continue to function unchanged

## Adding New Structure Types

To add a new structure type:

1. Create a new configuration file: `structure_{type}_config.json`
2. Define the boundary conditions and loads specific to that structure type
3. No code changes required - the system automatically loads structure-specific configurations

Example for a new structure type "2045":

```json
{
  "description": "Structure type 2045 configuration",
  "boundary_conditions_config": [
    {
      "type": "fixed_support",
      "named_selection": "gu_fixed"
    },
    {
      "type": "frictionless_support",
      "named_selection": "gu_frictionless"
    }
  ],
  "loads_config": [
    {
      "type": "pressure",
      "named_selection": "gu_pressure",
      "use_database": true
    },
    {
      "type": "temperature",
      "named_selection": "gu_temp",
      "value": 150
    }
  ]
}
```

## Troubleshooting

### Common Issues

**Issue**: Named selection not found
- **Solution**: Verify that the named selection exists in your ANSYS model and matches the name in the configuration exactly (case-sensitive)

**Issue**: Load values not applied
- **Solution**: Check that `use_database` is set correctly. If `true`, verify the load_database.json contains entries for your structure type and execution parameters

**Issue**: Unknown boundary condition type
- **Solution**: Ensure you're using one of the supported types listed in this guide

**Issue**: Configuration validation fails
- **Solution**: Run `validate_configuration()` to see detailed error messages and fix the issues before applying

## Best Practices

1. **Naming Conventions**: Use consistent named selection naming (e.g., `gu_` prefix for boundary conditions)
2. **Documentation**: Add a `description` field to your configuration files for clarity
3. **Validation First**: Always validate configurations before applying to catch issues early
4. **Database Organization**: Keep load_database.json organized by structure type for easy maintenance
5. **Incremental Testing**: Test new structure configurations on simple models before applying to complex assemblies
