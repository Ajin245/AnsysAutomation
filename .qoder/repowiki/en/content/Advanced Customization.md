# Advanced Customization

<cite>
**Referenced Files in This Document**   
- [structure_detector.py](file://core/structure_detector.py)
- [pattern_matching.py](file://utils/pattern_matching.py)
- [config_manager.py](file://config/config_manager.py)
- [named_selection_manager.py](file://core/named_selection_manager.py)
- [bolt_manager.py](file://managers/bolt_manager.py)
- [contact_manager.py](file://managers/contact_manager.py)
- [analysis_manager.py](file://managers/analysis_manager.py)
- [project_settings.json](file://config_files/project_settings.json)
- [contact_settings.json](file://config_files/contact_settings.json)
- [bolt_database.json](file://config_files/bolt_database.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Structure Type Detection and Configuration](#structure-type-detection-and-configuration)
3. [Pattern Matching System](#pattern-matching-system)
4. [Custom Configuration Files](#custom-configuration-files)
5. [Extending Detection Patterns](#extending-detection-patterns)
6. [Manager Class Customization](#manager-class-customization)
7. [Testing and Validation](#testing-and-validation)
8. [Best Practices for Collaboration](#best-practices-for-collaboration)

## Introduction
This document provides comprehensive guidance on advanced customization capabilities within the AnsysAutomation system. It details how to extend the system for new structure types, modify detection patterns, and enhance manager functionality. The system supports flexible configuration through JSON files and extensible Python classes, enabling users to adapt the automation framework to specialized analysis requirements without modifying core code.

## Structure Type Detection and Configuration

The system uses a hierarchical configuration approach where structure-specific settings can override base configurations. The `ConfigurationManager` class handles loading and merging of configurations, with structure-specific files taking precedence over default settings.

```mermaid
flowchart TD
Start([Start]) --> LoadBase["Load Base Configuration"]
LoadBase --> CheckStructure["Check for Structure-Specific Config"]
CheckStructure --> |Exists| LoadStructure["Load Structure-Specific Config"]
CheckStructure --> |Not Exists| UseBase["Use Base Configuration Only"]
LoadStructure --> Merge["Merge Configurations<br>(Structure Overrides Base)"]
Merge --> ReturnConfig["Return Merged Configuration"]
UseBase --> ReturnConfig
ReturnConfig --> End([End])
```

**Diagram sources**
- [config_manager.py](file://config/config_manager.py#L119-L159)

**Section sources**
- [config_manager.py](file://config/config_manager.py#L119-L159)

## Pattern Matching System

The pattern matching system provides flexible string matching capabilities without requiring external dependencies. The `simple_pattern_match` function supports wildcard matching with the asterisk (*) character, enabling pattern-based detection of model components.

```mermaid
classDiagram
class PatternMatching {
+simple_pattern_match(name, pattern) bool
+match_any_pattern(name, patterns) bool
+find_matching_names(names, pattern) list
+extract_number_from_name(entity_name) tuple
}
class StructureDetector {
+detect_structure_type() tuple
+analyze_ns_patterns() dict
+detect_load_configuration() dict
}
class NamedSelectionManager {
+get_ns_by_pattern(pattern) list
+get_ns_by_type(ns_type) list
}
PatternMatching <|-- StructureDetector : "uses"
PatternMatching <|-- NamedSelectionManager : "uses"
```

**Diagram sources**
- [pattern_matching.py](file://utils/pattern_matching.py#L8-L71)
- [structure_detector.py](file://core/structure_detector.py#L29-L115)
- [named_selection_manager.py](file://core/named_selection_manager.py#L39-L57)

**Section sources**
- [pattern_matching.py](file://utils/pattern_matching.py#L8-L71)
- [structure_detector.py](file://core/structure_detector.py#L6-L158)
- [named_selection_manager.py](file://core/named_selection_manager.py#L6-L190)

## Custom Configuration Files

Structure-specific configuration files allow overriding base settings for specialized analysis requirements. These files follow the naming convention `structure_{structure_type}_config.json` and are located in the configuration directory.

### Configuration Hierarchy
The system follows a specific hierarchy when loading configurations:
1. Load base configuration files
2. Check for structure-specific configuration
3. Merge configurations with structure-specific settings taking precedence

```mermaid
graph TD
A[Base Configuration] --> B[Project Settings]
A --> C[Mesh Configuration]
A --> D[Load Database]
A --> E[Analysis Scenarios]
A --> F[Bolt Database]
A --> G[Contact Settings]
H[Structure-Specific Configuration] --> I[structure_type_config.json]
I --> J{Override Settings}
B --> K[Merged Configuration]
C --> K
D --> K
E --> K
F --> K
G --> K
J --> K
```

**Diagram sources**
- [config_manager.py](file://config/config_manager.py#L119-L159)
- [paths.py](file://config/paths.py#L32-L43)

**Section sources**
- [config_manager.py](file://config/config_manager.py#L119-L159)
- [paths.py](file://config/paths.py#L32-L43)

## Extending Detection Patterns

### Modifying Structure Detection
The `StructureDetector` class uses regex patterns to identify structure types from model names. New patterns can be added to the `STRUCTURE_PATTERNS` dictionary to recognize additional structure types.

```mermaid
flowchart TD
A[Model Name] --> B{Apply Regex Patterns}
B --> C["r'^(\d+)-(\d{2})-F\d'"]
B --> D["r'^(custom_\d+)-(\d{2})-F\d'"]
B --> E["r'^(\d{3})_'"]
B --> F["r'^([A-Z]+)_'"]
B --> G[Add New Pattern]
C --> H[Standard Structure]
D --> I[Custom Structure]
E --> J[Legacy Structure]
F --> K[Coded Structure]
G --> L[New Structure Type]
```

**Diagram sources**
- [structure_detector.py](file://core/structure_detector.py#L13-L18)

**Section sources**
- [structure_detector.py](file://core/structure_detector.py#L13-L51)

### Customizing Contact Detection
Contact detection rules are defined in the `contact_settings.json` file and can be extended to handle new component types. Each rule specifies contact and target patterns, contact type, and associated properties.

```mermaid
classDiagram
class ContactRule {
+name : string
+contact_pattern : string
+target_pattern : string
+type : ContactType
+detection_method : ContactDetectionPoint
+interface_treatment : ContactInitialEffect
+friction_coefficient : float
+offset : float
}
class ContactManager {
+analyze_and_configure_contacts() void
+_configure_contact(contact) bool
+_find_contact_config(contact_bodies, target_bodies) dict
}
ContactManager --> ContactRule : "applies"
```

**Diagram sources**
- [contact_manager.py](file://managers/contact_manager.py#L60-L75)
- [contact_settings.json](file://config_files/contact_settings.json#L2-L130)

**Section sources**
- [contact_manager.py](file://managers/contact_manager.py#L8-L96)
- [contact_settings.json](file://config_files/contact_settings.json#L2-L130)

## Manager Class Customization

### Bolt Manager Extension
The `BoltManager` class can be extended to support new bolt detection patterns and pretension calculation methods. The system automatically detects bolt bodies based on naming conventions and retrieves appropriate pretension values from the bolt database.

```mermaid
sequenceDiagram
participant User as "User"
participant BoltManager as "BoltManager"
participant NSManager as "NamedSelectionManager"
participant Database as "Bolt Database"
User->>BoltManager : apply_bolt_loads()
BoltManager->>NSManager : get_ns_by_pattern("gu_bolt*_f")
NSManager-->>BoltManager : List of Bolt NS
loop For each Bolt Body
BoltManager->>BoltManager : get_correct_bolt_pretension()
BoltManager->>BoltManager : Search "mbolt(\d+)" in body name
alt Bolt Size Found
BoltManager->>Database : Lookup pretension by size
Database-->>BoltManager : Pretension value
else Default
BoltManager->>Database : Get default pretension
Database-->>BoltManager : Default value
end
BoltManager->>BoltManager : Create Bolt Pretension Load
end
BoltManager-->>User : List of created bolt loads
```

**Diagram sources**
- [bolt_manager.py](file://managers/bolt_manager.py#L17-L68)
- [named_selection_manager.py](file://core/named_selection_manager.py#L39-L57)

**Section sources**
- [bolt_manager.py](file://managers/bolt_manager.py#L9-L68)

### Contact Manager Enhancement
The `ContactManager` class can be customized to implement new contact configuration logic. The system evaluates contact pairs based on body naming patterns and applies appropriate settings from the contact rules.

```mermaid
flowchart TD
A[Start Contact Configuration] --> B[Get All Contact Pairs]
B --> C{More Contacts?}
C --> |Yes| D[Get Contact and Target Bodies]
D --> E[Find Matching Contact Rule]
E --> F{Rule Found?}
F --> |Yes| G[Apply Contact Configuration]
F --> |No| H[Apply Default Configuration]
G --> I[Mark as Configured]
H --> I
I --> C
C --> |No| J[End Configuration]
```

**Diagram sources**
- [contact_manager.py](file://managers/contact_manager.py#L14-L37)
- [contact_settings.json](file://config_files/contact_settings.json#L2-L130)

**Section sources**
- [contact_manager.py](file://managers/contact_manager.py#L8-L96)

## Testing and Validation

### Configuration Validation
The system includes comprehensive validation mechanisms to ensure configuration integrity. The `ConfigurationManager` validates required keys in configuration files, while the `validators.py` module provides additional validation functions.

```mermaid
flowchart TD
A[Start Validation] --> B[Check File Existence]
B --> C[Parse JSON Configuration]
C --> D{Configuration Type}
D --> |Project Settings| E[Validate Project Keys]
D --> |Mesh Config| F[Validate Mesh Keys]
D --> |Analysis Scenarios| G[Validate Scenario Keys]
D --> |Bolt Database| H[Validate Bolt Keys]
D --> |Contact Settings| I[Validate Contact Keys]
E --> J[Return Validated Config]
F --> J
G --> J
H --> J
I --> J
J --> K[End Validation]
```

**Diagram sources**
- [config_manager.py](file://config/config_manager.py#L52-L72)
- [validators.py](file://utils/validators.py#L26-L49)

**Section sources**
- [config_manager.py](file://config/config_manager.py#L52-L72)
- [validators.py](file://utils/validators.py#L6-L161)

## Best Practices for Collaboration

### Version Control Strategy
When working with custom configurations, follow these version control best practices:
- Store configuration files in version control
- Use descriptive names for structure-specific configurations
- Document changes to detection patterns
- Maintain backward compatibility when possible

### Team Collaboration Guidelines
For effective collaboration across engineering teams:
- Establish naming conventions for new structure types
- Create shared documentation for custom configurations
- Implement peer review for pattern modifications
- Test changes in isolated environments before deployment
- Maintain a registry of structure types and their configurations

**Section sources**
- [config_manager.py](file://config/config_manager.py#L119-L159)
- [structure_detector.py](file://core/structure_detector.py#L13-L18)
- [contact_settings.json](file://config_files/contact_settings.json#L2-L130)
- [bolt_database.json](file://config_files/bolt_database.json#L1-L47)
- [project_settings.json](file://config_files/project_settings.json#L1-L56)