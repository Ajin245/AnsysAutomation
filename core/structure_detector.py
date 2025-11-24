# -*- coding: utf-8 -*-
"""
Structure type detection from model name and Named Selections
"""

import re
from utils.pattern_matching import simple_pattern_match, match_any_pattern

class StructureDetector:
    """Detect structure type from model name and Named Selections"""
    
    # Common structure patterns
    STRUCTURE_PATTERNS = {
        r'^(\d+)-(\d{2})-F\d': "standard",      # e.g., "151-02-F2" -> "151"
        r'^(custom_\d+)-(\d{2})-F\d': "custom", # e.g., "custom_001-01-F1" -> "custom_001"
        r'^(\d{3})_': "legacy",                 # e.g., "151_something" -> "151"
        r'^([A-Z]+)_': "coded"                  # e.g., "ABC_001" -> "ABC"
    }
    
    # Named Selection patterns for analysis
    NS_ANALYSIS_PATTERNS = {
        "bolts": ["*bolt*", "*mbolt*", "*gaika*"],
        "pressure": ["*pressure*", "*nagruzka*"],
        "contact": ["*contact*", "*kontakt*", "*shov*"],
        "remote": ["*remote*", "*udal*"],
        "supports": ["*fixed*", "*opora*", "*support*"]
    }
    
    @staticmethod
    def detect_structure_type():
        """
        Determine structure type from model name patterns
        
        Returns:
            tuple: (structure_type, structure_category)
        """
        model_name = Model.Name
        
        # Try all patterns
        for pattern, category in StructureDetector.STRUCTURE_PATTERNS.items():
            match = re.match(pattern, model_name)
            if match:
                structure_type = match.group(1)
                return structure_type, category
        
        # Fallback: use first part of model name
        parts = model_name.split('-')
        if parts:
            return parts[0], "unknown"
        
        return "default", "unknown"
    
    @staticmethod
    def analyze_ns_patterns():
        """
        Analyze Named Selections patterns to detect configuration
        
        Returns:
            dict: Analysis results with boolean flags
        """
        all_ns = [ns.Name for ns in Model.NamedSelections.Children]
        
        analysis = {}
        for ns_type, patterns in StructureDetector.NS_ANALYSIS_PATTERNS.items():
            analysis["has_" + ns_type] = match_any_pattern(all_ns, patterns)
        
        # Additional analysis
        analysis["total_ns_count"] = len(all_ns)
        analysis["ns_names"] = all_ns
        
        return analysis
    
    @staticmethod
    def detect_load_configuration():
        """
        Detect load configuration based on Named Selections
        
        Returns:
            dict: Load configuration analysis
        """
        all_ns = [ns.Name for ns in Model.NamedSelections.Children]
        
        load_config = {
            "has_force_load": any(simple_pattern_match(ns, "*force*") for ns in all_ns),
            "has_moment_load": any(simple_pattern_match(ns, "*moment*") for ns in all_ns),
            "has_pressure_load": any(simple_pattern_match(ns, "*pressure*") for ns in all_ns),
            "has_temperature_load": any(simple_pattern_match(ns, "*temperature*") for ns in all_ns),
            "has_bearing_load": any(simple_pattern_match(ns, "*bearing*") for ns in all_ns)
        }
        
        return load_config
    
    @staticmethod
    def detect_boundary_conditions():
        """
        Detect boundary conditions based on Named Selections
        
        Returns:
            dict: Boundary conditions analysis
        """
        all_ns = [ns.Name for ns in Model.NamedSelections.Children]
        
        bc_config = {
            "has_fixed_support": any(simple_pattern_match(ns, "*fixed*") for ns in all_ns),
            "has_displacement": any(simple_pattern_match(ns, "*disp*") for ns in all_ns),
            "has_remote_displacement": any(simple_pattern_match(ns, "*remote_disp*") for ns in all_ns),
            "has_remote_force": any(simple_pattern_match(ns, "*remote_f*") for ns in all_ns),
            "has_frictionless": any(simple_pattern_match(ns, "*frictionless*") for ns in all_ns),
            "has_compression": any(simple_pattern_match(ns, "*compression*") for ns in all_ns)
        }
        
        return bc_config
    
    @staticmethod
    def get_model_info():
        """
        Get comprehensive model information
        
        Returns:
            dict: Complete model information
        """
        try:
            geometry = Model.Geometry
            bodies = geometry.GetChildren(DataModelObjectCategory.Body, True)
            
            model_info = {
                "name": Model.Name,
                "bodies_count": len(bodies),
                "body_names": [body.Name for body in bodies],
                "named_selections_count": len(Model.NamedSelections.Children),
                "material_count": len(Model.Materials.Children) if hasattr(Model, 'Materials') else 0
            }
            
            # Analyze body types
            body_types = {}
            for body in bodies:
                body_name_lower = body.Name.lower()
                if "mbolt" in body_name_lower:
                    body_types["bolts"] = body_types.get("bolts", 0) + 1
                elif "shaiba" in body_name_lower:
                    body_types["washers"] = body_types.get("washers", 0) + 1
                elif "mgaika" in body_name_lower:
                    body_types["nuts"] = body_types.get("nuts", 0) + 1
                elif "opora" in body_name_lower:
                    body_types["supports"] = body_types.get("supports", 0) + 1
                elif "truba" in body_name_lower:
                    body_types["pipes"] = body_types.get("pipes", 0) + 1
                elif "shov" in body_name_lower:
                    body_types["welds"] = body_types.get("welds", 0) + 1
                else:
                    body_types["other"] = body_types.get("other", 0) + 1
            
            model_info["body_types"] = body_types
            return model_info
            
        except Exception as e:
            print("Warning: Could not get complete model info: " + str(e))
            return {"name": Model.Name, "error": str(e)}