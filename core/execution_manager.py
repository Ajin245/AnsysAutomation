# -*- coding: utf-8 -*-
"""
Execution type manager for load determination
"""

import re
from utils.validators import validate_execution_type

class ExecutionManager:
    """Execution type manager"""
    
    def __init__(self, project_settings, load_database, analysis_scenarios):
        self.project_settings = project_settings
        self.load_database = load_database
        self.analysis_scenarios = analysis_scenarios
    
    def determine_execution_type(self):
        """
        Determine execution type from model name
        
        Returns:
            str: Execution type identifier
            
        Raises:
            System.Exception: If cannot determine execution type
        """
        geometry_name = Model.Name
        
        # Try structure-specific pattern first
        structure_pattern = self.project_settings["execution"].get("name_pattern")
        if structure_pattern:
            match = re.match(structure_pattern, geometry_name)
            if match:
                return match.group(1)
        
        # Fallback to default pattern
        default_pattern = self.project_settings["execution"].get("default_pattern", r"(\d{2}-\d{2}-[Ff]\d)")
        match = re.match(default_pattern, geometry_name)
        if match:
            return match.group(1)
        
        # Try alternative patterns
        alternative_patterns = [
            r"(\d{3}-\d{2}-[Ff]\d)",      # e.g., "151-02-F1"
            r"([A-Za-z]+_\d+-\d{2}-[Ff]\d)", # e.g., "custom_001-02-F1"
            r"(\d{2}-\d{2})",              # e.g., "02-02"
            r"(\d{3})"                     # e.g., "151"
        ]
        
        for pattern in alternative_patterns:
            match = re.match(pattern, geometry_name)
            if match:
                return match.group(1)
        
        # Final fallback
        default_execution = self.project_settings["execution"].get("default_execution")
        if default_execution:
            return default_execution
        
        raise System.Exception("Failed to determine execution type from model name: " + str(geometry_name))
    
    def validate_execution(self, execution_type):
        """
        Validate execution existence in load database
        
        Args:
            execution_type (str): Execution type to validate
            
        Returns:
            tuple: (execution_number, load_group) if valid
            
        Raises:
            System.Exception: If execution type is invalid
        """
        return validate_execution_type(execution_type, self.load_database)
    
    def get_load_configuration(self, execution_type):
        """
        Get load configuration for execution type
        
        Args:
            execution_type (str): Execution type
            
        Returns:
            dict: Load configuration
            
        Raises:
            System.Exception: If execution type is invalid
        """
        execution_number, load_group = self.validate_execution(execution_type)
        
        execution_loads = self.load_database[execution_number]
        load_case = execution_loads[load_group]
        
        load_config = {
            "execution_number": execution_number,
            "load_group": load_group,
            "forces": load_case["nominal_forces"],
            "moments": load_case.get("nominal_moments", {"mx": 0, "my": 0, "mz": 0})
        }
        
        # Add pressure if specified in load case
        if "pressure" in load_case:
            load_config["pressure"] = load_case["pressure"]
        
        return load_config
    
    def _get_load_factors(self, scenario_name="standard_sequence"):
        """
        Get load factors for analysis scenario
        
        Args:
            scenario_name (str): Analysis scenario name
            
        Returns:
            list: Load factors
        """
        scenario = self.analysis_scenarios.get(scenario_name)
        if not scenario:
            raise System.Exception("Analysis scenario not found: " + str(scenario_name))

        load_factors = scenario.get("load_factors")
        if load_factors is None:
            raise System.Exception("Scenario has no 'load_factors': " + str(scenario_name))

        return load_factors
    
    def get_available_executions(self):
        """
        Get list of available executions in load database
        
        Returns:
            list: Available execution numbers
        """
        return list(self.load_database.keys())
    
    def get_available_load_groups(self, execution_number):
        """
        Get available load groups for execution
        
        Args:
            execution_number (str): Execution number
            
        Returns:
            list: Available load groups
            
        Raises:
            System.Exception: If execution number not found
        """
        if execution_number not in self.load_database:
            raise System.Exception("Execution " + str(execution_number) + " not found in load database")
        
        return list(self.load_database[execution_number].keys())
