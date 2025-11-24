# -*- coding: utf-8 -*-
"""
Path configuration for ANSYS Automation
"""

import System
from System.IO import Path

# Base configuration path
CONFIG_PATH = "E:\\OLEGG\\Other\\"

# Configuration file names
PROJECT_SETTINGS_FILE = "project_settings.json"
MESH_CONFIG_FILE = "mesh_config.json"
LOAD_DATABASE_FILE = "load_database.json"
ANALYSIS_SCENARIOS_FILE = "analysis_scenarios.json"
BOLT_DATABASE_FILE = "bolt_database.json"
CONTACT_SETTINGS_FILE = "contact_settings.json"

def get_config_file_path(filename):
    """
    Get full path for configuration file
    
    Args:
        filename (str): Configuration file name
        
    Returns:
        str: Full path to configuration file
    """
    return Path.Combine(CONFIG_PATH, filename)

def get_structure_config_path(structure_type):
    """
    Get path for structure-specific configuration
    
    Args:
        structure_type (str): Structure type identifier
        
    Returns:
        str: Full path to structure-specific config file
    """
    filename = f"structure_{structure_type}_config.json"
    return get_config_file_path(filename)

def validate_config_path():
    """
    Validate that configuration path exists
    
    Returns:
        bool: True if path exists
        
    Raises:
        System.Exception: If configuration path doesn't exist
    """
    if not System.IO.Directory.Exists(CONFIG_PATH):
        raise System.Exception(f"Configuration path does not exist: {CONFIG_PATH}")
    return True

def get_all_config_files():
    """
    Get list of all main configuration files
    
    Returns:
        list: List of configuration file paths
    """
    return [
        get_config_file_path(PROJECT_SETTINGS_FILE),
        get_config_file_path(MESH_CONFIG_FILE),
        get_config_file_path(LOAD_DATABASE_FILE),
        get_config_file_path(ANALYSIS_SCENARIOS_FILE),
        get_config_file_path(BOLT_DATABASE_FILE),
        get_config_file_path(CONTACT_SETTINGS_FILE)
    ]