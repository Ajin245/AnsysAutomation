# -*- coding: utf-8 -*-
"""
Contact pairs configuration manager for ANSYS Automation
"""

from utils.pattern_matching import simple_pattern_match

class ContactManager:
    """Contact pairs configuration manager"""
    
    def __init__(self, contact_settings):
        self.contact_settings = contact_settings
    
    def analyze_and_configure_contacts(self):
        """Configure contact pairs automatically"""
        try:
            print("Configuring automatic contacts...")
            
            connections = Model.Connections
            contacts = connections.Children
            
            if contacts.Count > 0:
                connection_group = DataModel.GetObjectById(contacts[0].ObjectId)
                connection_group.ToleranceType = ContactToleranceType.Value
                connection_group.ToleranceValue = Quantity(0.5, "mm")
                
                Model.Connections.CreateAutomaticConnections()
                
                configured_count = 0
                for contact in connection_group.Children:
                    if contact.__class__.__name__ == "ContactRegion":
                        contact.RenameBasedOnDefinition()
                        if self._configure_contact(contact):
                            configured_count += 1
                
                print("Successfully configured " + str(configured_count) + " contact pairs")
                
        except Exception as e:
            print("Warning during contact configuration: " + str(e))
    
    def _configure_contact(self, contact):
        """Configure individual contact pair"""
        try:
            contact_bodies = contact.ContactBodies
            target_bodies = contact.TargetBodies
            
            if not contact_bodies or not target_bodies:
                return False
            
            config = self._find_contact_config(contact_bodies, target_bodies)
            if config:
                self._apply_contact_config(contact, config)
                return True
            return False
                
        except Exception as e:
            print("Error configuring contact: " + str(e))
            return False
    
    def _find_contact_config(self, contact_bodies, target_bodies):
        """Find contact configuration based on body names"""
        for config in self.contact_settings["contact_rules"]:
            if self._matches_config(contact_bodies, target_bodies, config):
                return config
        return None
    
    def _matches_config(self, contact_bodies, target_bodies, config):
        """Check if bodies match configuration patterns"""
        contact_pattern = config["contact_pattern"]
        target_pattern = config["target_pattern"]
        
        contact_match = any(simple_pattern_match(body.Name, contact_pattern) for body in contact_bodies)
        target_match = any(simple_pattern_match(body.Name, target_pattern) for body in target_bodies)
        
        return contact_match and target_match
    
    def _apply_contact_config(self, contact, config):
        """Apply configuration to contact pair"""
        try:
            contact_type = getattr(ContactType, config["type"])
            contact.ContactType = contact_type
            
            if contact_type == ContactType.Frictional:
                contact.FrictionCoefficient = config["friction_coefficient"]
            
            detection_method = getattr(ContactDetectionPoint, config["detection_method"])
            contact.DetectionMethod = detection_method
            
            interface_treatment = getattr(ContactInitialEffect, config["interface_treatment"])
            contact.InterfaceTreatment = interface_treatment
            
            if contact_type == ContactType.Frictional and "offset" in config:
                contact.UserOffset = Quantity(config["offset"], "mm")
                
        except Exception as e:
            print("Error applying contact configuration: " + str(e))