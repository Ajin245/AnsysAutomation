# -*- coding: utf-8 -*-
"""
Constants for ANSYS Automation
"""

# Default settings for fallback
DEFAULT_SETTINGS = {
    "project": {
        "name": "Типовая опорная конструкция",
        "version": "2.2", 
        "description": "Автоматизированная настройка расчетов опорных конструкций"
    },
    "execution": {
        "name_pattern": r"(\d{2}-\d{2}-[Ff]\d)",
        "default_execution": "05-50-F2"
    },
    "boundary_conditions": {
        "fixed_support": "gu_fixed",
        "displacement": "gu_disp", 
        "remote_displacement": "gu_remote_disp",
        "remote_force": "gu_remote_f"
    },
    "loads": {
        "force": "gu_force",
        "moment": "gu_moment",
        "pressure": "gu_pressure", 
        "bolt_pattern": "gu_bolt*_f"
    },
    "mesh_settings": {
        "default_element_order": "Linear",
        "result_keywords": ["shov", "bolt", "opora", "truba", "osnovanie"]
    }
}

# Required keys for configuration validation
REQUIRED_KEYS = {
    "project_settings": ["project", "execution", "boundary_conditions", "loads"],
    "mesh_config": ["mesh_settings"],
    "analysis_scenarios": ["standard_sequence"],
    "bolt_database": ["default"],
    "contact_settings": ["contact_rules"]
}

# Analysis scenario defaults
DEFAULT_ANALYSIS_SCENARIO = {
    "name": "Стандартная последовательность",
    "description": "3 шага: предзатяжка + номинальная нагрузка + проектное землетрясение", 
    "steps": 3,
    "load_factors": [0.5, 1.0, 1.5],
    "analysis_settings": {
        "large_deflection": True,
        "newton_raphson": "Unsymmetric",
        "nodal_forces": "Yes",
        "general_miscellaneous": True,
        "contact_miscellaneous": True
    }
}

# Bolt database defaults  
DEFAULT_BOLT_PRETENSION = 1350
DEFAULT_BOLT_DIAMETER = 6

# Contact settings defaults
DEFAULT_CONTACT_SETTINGS = {
    "contact_rules": [
        {
            "name": "default_frictional",
            "contact_pattern": "*",
            "target_pattern": "*", 
            "type": "Frictional",
            "detection_method": "ProgramControlled",
            "interface_treatment": "AdjustToTouch",
            "friction_coefficient": 0.3
        }
    ],
    "advanced_settings": {
        "formulation": "AugmentedLagrange",
        "normal_stiffness": "ProgramControlled",
        "update_stiffness": "EachIteration", 
        "stabilization": "None"
    }
}

# Mesh settings defaults
DEFAULT_MESH_SETTINGS = {
    "meshCoef": 4.0,
    "meshMethod": "MultiZone", 
    "elementOrder": "ProgramControlled"
}

# Units
UNITS = {
    "force": "N",
    "moment": "N·mm",
    "pressure": "MPa", 
    "length": "mm",
    "time": "s",
    "angle": "rad"
}