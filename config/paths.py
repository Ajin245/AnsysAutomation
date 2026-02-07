# -*- coding: utf-8 -*-
"""
Path configuration for ANSYS Automation
"""

import System
from System.IO import Path

CONFIG_PATH_ENV_VAR = "ANSYS_AUTOMATION_CONFIG_PATH"


def _get_repository_default_config_path():
    """Get default config path relative to repository root."""
    current_dir = Path.GetDirectoryName(Path.GetFullPath(__file__))
    return Path.GetFullPath(Path.Combine(current_dir, "..", "config_files"))


def resolve_config_path(config_path=None):
    """
    Resolve active configuration path.

    Priority:
    1) Explicit ``config_path`` argument
    2) Environment variable ``ANSYS_AUTOMATION_CONFIG_PATH``
    3) Repository relative default ``config_files/``
    """
    if config_path:
        return config_path

    env_path = System.Environment.GetEnvironmentVariable(CONFIG_PATH_ENV_VAR)
    if env_path:
        return env_path

    return _get_repository_default_config_path()


# Base configuration path (kept for backwards compatibility with existing imports)
CONFIG_PATH = resolve_config_path()

# Configuration file names
PROJECT_SETTINGS_FILE = "project_settings.json"
MESH_CONFIG_FILE = "mesh_config.json"
LOAD_DATABASE_FILE = "load_database.json"
ANALYSIS_SCENARIOS_FILE = "analysis_scenarios.json"
BOLT_DATABASE_FILE = "bolt_database.json"
CONTACT_SETTINGS_FILE = "contact_settings.json"

def get_config_file_path(filename, config_path=None):
    """
    Get full path for configuration file
    
    Args:
        filename (str): Configuration file name
        
    Returns:
        str: Full path to configuration file
    """
    return Path.Combine(resolve_config_path(config_path), filename)

def get_structure_config_path(structure_type, config_path=None):
    """
    Get path for structure-specific configuration
    
    Args:
        structure_type (str): Structure type identifier
        
    Returns:
        str: Full path to structure-specific config file
    """
    filename = f"structure_{structure_type}_config.json"
    return get_config_file_path(filename, config_path=config_path)

def validate_config_path(config_path=None):
    """
    Validate that configuration path exists
    
    Returns:
        bool: True if path exists
        
    Raises:
        System.Exception: If configuration path doesn't exist
    """
    resolved_path = resolve_config_path(config_path)
    if not System.IO.Directory.Exists(resolved_path):
        raise System.Exception(
            "Configuration path does not exist: {0}. "
            "Set environment variable {1} or pass custom path via "
            "ConfigurationManager(config_path='...').".format(
                resolved_path,
                CONFIG_PATH_ENV_VAR
            )
        )
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
