# -*- coding: utf-8 -*-
"""
Validation utilities for ANSYS Automation
"""

import System
from System.IO import File

def validate_file_exists(file_path):
    """
    Validate that file exists
    
    Args:
        file_path (str): Path to file
        
    Returns:
        bool: True if file exists
        
    Raises:
        System.Exception: If file doesn't exist
    """
    if not File.Exists(file_path):
        raise System.Exception("File not found: " + file_path)
    return True

def validate_required_keys(config_dict, required_keys, context=""):
    """
    Validate that required keys exist in configuration dictionary
    
    Args:
        config_dict (dict): Configuration dictionary to validate
        required_keys (list): List of required keys
        context (str): Context for error message
        
    Returns:
        bool: True if all keys are present
        
    Raises:
        System.Exception: If required keys are missing
    """
    missing_keys = []
    for key in required_keys:
        if key not in config_dict:
            missing_keys.append(key)
    
    if missing_keys:
        error_msg = "Missing required keys" + str(context) + ": " + ', '.join(missing_keys)
        raise System.Exception(error_msg)
    
    return True

def validate_named_selection(ns_name, all_named_selections):
    """
    Validate that named selection exists
    
    Args:
        ns_name (str): Named selection name
        all_named_selections: Collection of all named selections
        
    Returns:
        bool: True if named selection exists
    """
    if not ns_name:
        return False
        
    return any(ns.Name == ns_name for ns in all_named_selections)

def validate_model_structure():
    """
    Validate basic model structure requirements
    
    Returns:
        bool: True if model structure is valid
    """
    try:
        # Check if Model object is available
        if not Model:
            raise System.Exception("Model object not available")
        
        # Check if Geometry exists
        if not Model.Geometry:
            raise System.Exception("Model geometry not available")
            
        # Check if Named Selections exist
        if not Model.NamedSelections:
            raise System.Exception("Named Selections not available")
            
        return True
        
    except Exception as e:
        raise System.Exception("Model structure validation failed: " + str(e))

def validate_mesh_settings(mesh_settings):
    """
    Validate mesh settings configuration
    
    Args:
        mesh_settings (dict): Mesh settings dictionary
        
    Returns:
        bool: True if mesh settings are valid
    """
    required_mesh_keys = ["meshCoef", "meshMethod", "elementOrder"]
    
    for key, settings in mesh_settings.items():
        if not all(k in settings for k in required_mesh_keys):
            raise System.Exception("Invalid mesh settings for '" + str(key) + "'. Required: " + str(required_mesh_keys))
    
    return True

def validate_contact_settings(contact_settings):
    """
    Validate contact settings configuration
    
    Args:
        contact_settings (dict): Contact settings dictionary
        
    Returns:
        bool: True if contact settings are valid
    """
    if "contact_rules" not in contact_settings:
        raise System.Exception("Missing 'contact_rules' in contact settings")
    
    required_contact_keys = ["contact_pattern", "target_pattern", "type", "detection_method"]
    
    for i, rule in enumerate(contact_settings["contact_rules"]):
        missing_keys = [k for k in required_contact_keys if k not in rule]
        if missing_keys:
            raise System.Exception("Contact rule " + str(i) + " missing keys: " + str(missing_keys))
    
    return True

def validate_execution_type(execution_type, load_database):
    """
    Validate execution type exists in load database
    
    Args:
        execution_type (str): Execution type to validate
        load_database (dict): Load database
        
    Returns:
        tuple: (execution_number, load_group) if valid
        
    Raises:
        System.Exception: If execution type is invalid
    """
    parts = execution_type.split('-')
    if len(parts) >= 3:
        execution_number = parts[0]
        load_group = parts[2].upper()
    else:
        execution_number = parts[0] if len(parts) > 0 else execution_type
        load_group = "F1"
    
    if execution_number not in load_database:
        raise System.Exception("Loads not found for execution " + execution_number)
    
    if load_group not in load_database[execution_number]:
        raise System.Exception("Load group " + load_group + " not found for execution " + execution_number)
    
    return execution_number, load_group