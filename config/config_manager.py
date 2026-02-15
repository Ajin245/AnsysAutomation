# -*- coding: utf-8 -*-
"""
Project configuration manager with hierarchy support
"""

import System
from System.IO import File, StreamReader

from utils.json_parser import load_json_file
from utils.validators import validate_file_exists, validate_required_keys
from .paths import CONFIG_PATH, get_config_file_path, get_structure_config_path, validate_config_path
from .constants import DEFAULT_SETTINGS, REQUIRED_KEYS

class ConfigurationManager:
    """Project configuration manager with hierarchy support"""
    
    def __init__(self, config_path=None):
        """
        Initialize ConfigurationManager
        
        Args:
            config_path (str): Optional custom configuration path
        """
        self.config_path = config_path or CONFIG_PATH
        validate_config_path(self.config_path)
    
    def load_config(self, file_path):
        """
        Load configuration file with existence check and validation
        
        Args:
            file_path (str): Path to configuration file
            
        Returns:
            dict: Parsed configuration
            
        Raises:
            System.Exception: If file not found or invalid
        """
        validate_file_exists(file_path)
        
        try:
            config_data = load_json_file(file_path)
            
            # Validate required keys based on file type
            self._validate_config_structure(file_path, config_data)
            
            return config_data
            
        except Exception as e:
            raise System.Exception(f"Error loading {file_path}: {str(e)}")
    
    def _validate_config_structure(self, file_path, config_data):
        """
        Validate configuration structure based on file type
        
        Args:
            file_path (str): Path to configuration file
            config_data (dict): Configuration data to validate
        """
        filename = System.IO.Path.GetFileName(file_path).lower()
        
        if "project_settings" in filename:
            validate_required_keys(config_data, REQUIRED_KEYS["project_settings"], " in project settings")
        elif "mesh_config" in filename:
            validate_required_keys(config_data, REQUIRED_KEYS["mesh_config"], " in mesh config")
        elif "analysis_scenarios" in filename:
            validate_required_keys(config_data, REQUIRED_KEYS["analysis_scenarios"], " in analysis scenarios")
        elif "bolt_database" in filename:
            validate_required_keys(config_data, REQUIRED_KEYS["bolt_database"], " in bolt database")
        elif "contact_settings" in filename:
            validate_required_keys(config_data, REQUIRED_KEYS["contact_settings"], " in contact settings")
    
    def load_project_settings(self):
        """Load main project settings"""
        file_path = get_config_file_path("project_settings.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_mesh_config(self):
        """Load mesh configuration"""
        file_path = get_config_file_path("mesh_config.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_load_database(self):
        """Load load database"""
        file_path = get_config_file_path("load_database.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_analysis_scenarios(self):
        """Load analysis scenarios"""
        file_path = get_config_file_path("analysis_scenarios.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_bolt_database(self):
        """Load bolt database"""
        file_path = get_config_file_path("bolt_database.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_contact_settings(self):
        """Load contact settings"""
        file_path = get_config_file_path("contact_settings.json", config_path=self.config_path)
        return self.load_config(file_path)
    
    def load_all_configs(self):
        """
        Load all main configuration files
        
        Returns:
            dict: Dictionary with all configurations
        """
        return {
            "project_settings": self.load_project_settings(),
            "mesh_config": self.load_mesh_config(),
            "load_database": self.load_load_database(),
            "analysis_scenarios": self.load_analysis_scenarios(),
            "bolt_database": self.load_bolt_database(),
            "contact_settings": self.load_contact_settings()
        }
    
    def load_structure_config(self, structure_type):
        """
        Load structure-specific configuration if exists
        
        Args:
            structure_type (str): Structure type identifier
            
        Returns:
            dict: Structure configuration or None if not exists
        """
        structure_config_file = get_structure_config_path(structure_type, config_path=self.config_path)
        if File.Exists(structure_config_file):
            try:
                return self.load_config(structure_config_file)
            except Exception as e:
                print(f"Warning: Failed to load structure config for {structure_type}: {str(e)}")
                return None
        return None
    
    def merge_configs(self, base_config, structure_config):
        """
        Merge structure config into base config (structure has priority)
        
        Args:
            base_config (dict): Base configuration
            structure_config (dict): Structure-specific configuration
            
        Returns:
            dict: Merged configuration
        """
        if not structure_config:
            return base_config
            
        merged = base_config.copy()
        for key, value in structure_config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Recursive merge for dictionaries
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def create_default_config(self, config_type):
        """
        Create default configuration for given type
        
        Args:
            config_type (str): Type of configuration
            
        Returns:
            dict: Default configuration
        """
        defaults = {
            "project_settings": DEFAULT_SETTINGS,
            "mesh_config": {"mesh_settings": {}},
            "analysis_scenarios": {"standard_sequence": DEFAULT_ANALYSIS_SCENARIO},
            "bolt_database": {"default": {"diameter": DEFAULT_BOLT_DIAMETER, "pretension": DEFAULT_BOLT_PRETENSION}},
            "contact_settings": DEFAULT_CONTACT_SETTINGS
        }
        
        return defaults.get(config_type, {})
    
    def validate_config_hierarchy(self, structure_type):
        """
        Validate that all required configuration files exist
        
        Args:
            structure_type (str): Structure type for validation
            
        Returns:
            tuple: (bool, list) - (is_valid, list_of_missing_files)
        """
        required_files = [
            get_config_file_path("project_settings.json", config_path=self.config_path),
            get_config_file_path("mesh_config.json", config_path=self.config_path), 
            get_config_file_path("load_database.json", config_path=self.config_path),
            get_config_file_path("analysis_scenarios.json", config_path=self.config_path),
            get_config_file_path("bolt_database.json", config_path=self.config_path),
            get_config_file_path("contact_settings.json", config_path=self.config_path)
        ]
        
        missing_files = []
        for file_path in required_files:
            if not File.Exists(file_path):
                missing_files.append(System.IO.Path.GetFileName(file_path))
        
        # Check for structure-specific config (optional)
        structure_config_file = get_structure_config_path(structure_type, config_path=self.config_path)
        has_structure_config = File.Exists(structure_config_file)
        
        return len(missing_files) == 0, missing_files, has_structure_config