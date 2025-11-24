# -*- coding: utf-8 -*-
"""
Manager for Named Selections operations
"""

from utils.pattern_matching import simple_pattern_match, find_matching_names
from utils.validators import validate_named_selection

class NamedSelectionManager:
    """Manager for Named Selections operations"""
    
    def __init__(self, project_settings):
        self.project_settings = project_settings
        self.all_ns = Model.NamedSelections.Children
        self.ns_cache = {}
    
    def get_ns_by_name(self, ns_name):
        """
        Get Named Selection by name with caching
        
        Args:
            ns_name (str): Named Selection name
            
        Returns:
            object: Named Selection object or None if not found
        """
        if not ns_name:  # Handle empty names
            return None
            
        if ns_name in self.ns_cache:
            return self.ns_cache[ns_name]
        
        for ns in self.all_ns:
            if ns.Name == ns_name:
                self.ns_cache[ns_name] = ns
                return ns
        return None
    
    def get_ns_by_pattern(self, pattern):
        """
        Find Named Selections by pattern using simple string matching
        
        Args:
            pattern (str): Pattern to match (supports *)
            
        Returns:
            list: List of matching Named Selections
        """
        if not pattern:
            return []
            
        matched_ns = []
        for ns in self.all_ns:
            if simple_pattern_match(ns.Name, pattern):
                matched_ns.append(ns)
        return matched_ns
    
    def validate_required_ns(self):
        """
        Validate that required Named Selections exist
        
        Returns:
            bool: True if all required NS exist, False otherwise
        """
        missing_ns = []
        
        # Check boundary conditions NS
        bc_settings = self.project_settings["boundary_conditions"]
        for bc_type, ns_name in bc_settings.items():
            if ns_name and not self.get_ns_by_name(ns_name):
                missing_ns.append(f"{bc_type}: {ns_name}")
        
        # Check loads NS
        load_settings = self.project_settings["loads"]
        for load_type, ns_name in load_settings.items():
            if ns_name and not self.get_ns_by_name(ns_name):
                missing_ns.append(f"{load_type}: {ns_name}")
        
        if missing_ns:
            message = "Missing Named Selections:\n" + "\n".join(f"  - {ns}" for ns in missing_ns)
            print("WARNING: " + message)
            return False
        
        return True
    
    def get_all_ns_names(self):
        """
        Get all Named Selection names
        
        Returns:
            list: List of all Named Selection names
        """
        return [ns.Name for ns in self.all_ns]
    
    def get_ns_by_type(self, ns_type):
        """
        Get Named Selections by type (load, bc, etc.)
        
        Args:
            ns_type (str): Type of Named Selection
            
        Returns:
            list: List of matching Named Selections
        """
        type_patterns = {
            "load": ["*force*", "*moment*", "*pressure*", "*bearing*", "*temperature*"],
            "bc": ["*fixed*", "*disp*", "*support*", "*frictionless*", "*compression*"],
            "bolt": ["*bolt*", "*mbolt*", "*gaika*"],
            "contact": ["*contact*", "*shov*"],
            "remote": ["*remote*"]
        }
        
        patterns = type_patterns.get(ns_type, [])
        matched_ns = []
        
        for pattern in patterns:
            matched_ns.extend(self.get_ns_by_pattern(pattern))
        
        # Remove duplicates
        return list(set(matched_ns))
    
    def find_ns_with_keywords(self, keywords):
        """
        Find Named Selections containing specific keywords
        
        Args:
            keywords (list): List of keywords to search for
            
        Returns:
            list: List of matching Named Selections
        """
        matched_ns = []
        for ns in self.all_ns:
            if any(keyword in ns.Name for keyword in keywords):
                matched_ns.append(ns)
        return matched_ns
    
    def validate_ns_for_analysis(self):
        """
        Comprehensive validation of Named Selections for analysis
        
        Returns:
            dict: Validation results
        """
        validation_result = {
            "has_required_ns": self.validate_required_ns(),
            "total_ns_count": len(self.all_ns),
            "load_ns": len(self.get_ns_by_type("load")),
            "bc_ns": len(self.get_ns_by_type("bc")),
            "bolt_ns": len(self.get_ns_by_type("bolt")),
            "missing_ns": self._get_missing_ns_details()
        }
        
        return validation_result
    
    def _get_missing_ns_details(self):
        """
        Get detailed information about missing Named Selections
        
        Returns:
            dict: Missing NS details
        """
        missing_details = {
            "boundary_conditions": [],
            "loads": []
        }
        
        # Check boundary conditions
        bc_settings = self.project_settings["boundary_conditions"]
        for bc_type, ns_name in bc_settings.items():
            if ns_name and not self.get_ns_by_name(ns_name):
                missing_details["boundary_conditions"].append({
                    "type": bc_type,
                    "expected_name": ns_name
                })
        
        # Check loads
        load_settings = self.project_settings["loads"]
        for load_type, ns_name in load_settings.items():
            if ns_name and not self.get_ns_by_name(ns_name):
                missing_details["loads"].append({
                    "type": load_type,
                    "expected_name": ns_name
                })
        
        return missing_details
    
    def clear_cache(self):
        """Clear Named Selection cache"""
        self.ns_cache.clear()