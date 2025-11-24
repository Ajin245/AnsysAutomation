# -*- coding: utf-8 -*-
"""
Bolt connections manager for ANSYS Automation
"""

import re
from utils.pattern_matching import simple_pattern_match

class BoltManager:
    """Bolt connections manager"""
    
    def __init__(self, bolt_database, project_settings, named_selection_manager):
        self.bolt_database = bolt_database
        self.project_settings = project_settings
        self.ns_manager = named_selection_manager
    
    def has_bolts(self):
        """Check if there are any bolts in the model"""
        bolt_pattern = self.project_settings["loads"].get("bolt_pattern", "gu_bolt*_f")
        bolt_ns_list = self.ns_manager.get_ns_by_pattern(bolt_pattern)
        return len(bolt_ns_list) > 0
        
    def get_correct_bolt_pretension(self):
        """Get correct bolt pretension by analyzing mbolt bodies in model"""
        all_bodies = Model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
        
        for body in all_bodies:
            body_name = body.Name
            if "mbolt" in body_name.lower():
                diameter_match = re.search(r'mbolt(\d+(?:\.\d+)?)', body_name, re.IGNORECASE)
                if diameter_match:
                    bolt_size = diameter_match.group(1)
                    if bolt_size in self.bolt_database:
                        pretension = self.bolt_database[bolt_size]["pretension"]
                        print("DEBUG: Using pretension from " + body_name + ": " + str(pretension) + "N")
                        return pretension
        
        # Fallback
        default_pretension = self.bolt_database.get("default", {}).get("pretension", 1350)
        print("DEBUG: Using default pretension: " + str(default_pretension) + "N")
        return default_pretension
        
    def apply_bolt_loads(self, analysis, steps_count):
        """Apply bolt loads with proper step configuration"""
        bolt_pattern = self.project_settings["loads"].get("bolt_pattern", "gu_bolt*_f")
        bolt_ns_list = self.ns_manager.get_ns_by_pattern(bolt_pattern)
        
        bolt_loads = []
        for ns in bolt_ns_list:
            try:
                bolt_pretension = self.get_correct_bolt_pretension()
                
                bolt = analysis.AddBoltPretension()
                bolt.Location = ns
                
                # Step 0 - pretension
                bolt.Preload.Output.SetDiscreteValue(0, Quantity(bolt_pretension, "N"))
                
                # Other steps - lock
                for i in range(2, steps_count):
                    bolt.SetDefineBy(i, BoltLoadDefineBy.Lock)
                
                bolt_loads.append(bolt)
                print("Created load for bolt NS " + ns.Name + " with pretension " + str(bolt_pretension) + "N")
            except Exception as e:
                print("Warning: Failed to create load for bolt NS " + ns.Name + ": " + str(e))
        
        return bolt_loads