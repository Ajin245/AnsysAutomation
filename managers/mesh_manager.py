# -*- coding: utf-8 -*-
"""
Mesh settings manager for ANSYS Automation
"""

import re
from utils.pattern_matching import simple_pattern_match, extract_number_from_name

class MeshManager:
    """Mesh settings manager"""
    
    def __init__(self, mesh_config, project_settings):
        self.mesh_config = mesh_config
        self.project_settings = project_settings
        if "mesh_settings" in mesh_config:
            self.sorted_keys = sorted(mesh_config["mesh_settings"].keys(), key=lambda x: len(x), reverse=True)
        else:
            self.sorted_keys = []
    
    def apply_mesh_settings(self):
        """Apply mesh settings to all Named Selections"""
        mesh = Model.Mesh
        mesh.ElementOrder = ElementOrder.Linear
        
        all_ns = Model.NamedSelections.Children
        
        for ns in all_ns:
            if self._is_load_or_bc_ns(ns.Name):
                continue
                
            try:
                mesh_settings = self._get_mesh_settings(ns.Name)
                if mesh_settings:
                    self._create_sizing_and_method(ns, mesh_settings)
            except Exception as e:
                print("Warning during mesh creation for " + ns.Name + ": " + str(e))
        
        mesh.GroupAllSimilarChildren()
        mesh.GenerateMesh()
    
    def _is_load_or_bc_ns(self, ns_name):
        """Check if NS is for load or boundary condition"""
        bc_settings = self.project_settings["boundary_conditions"]
        load_settings = self.project_settings["loads"]
        
        all_special_ns = []
        for ns_list in [bc_settings, load_settings]:
            for ns_name_val in ns_list.values():
                if ns_name_val:
                    all_special_ns.append(ns_name_val)
        
        bolt_pattern = self.project_settings["loads"].get("bolt_pattern", "gu_bolt*_f")
        if simple_pattern_match(ns_name, bolt_pattern):
            return True
                
        return ns_name in all_special_ns
            
    def _get_mesh_settings(self, ns_name):
        """Get mesh settings for Named Selection"""
        if not ns_name or "mesh_settings" not in self.mesh_config:
            return None
            
        parsed = extract_number_from_name(ns_name)
        if not parsed:
            return None
            
        base_name = parsed[0]
        
        for key in self.sorted_keys:
            if key == base_name or key in base_name:
                return self.mesh_config["mesh_settings"][key]
        
        return None
    
    def _create_sizing_and_method(self, ns, mesh_settings):
        """Create sizing and method for Named Selection"""
        mesh = Model.Mesh
        
        sizing = mesh.AddSizing()
        sizing.Location = ns
        sizing.RenameBasedOnDefinition()
        
        parsed = extract_number_from_name(ns.Name)
        if parsed:
            dimension = parsed[1]
            mesh_coef = mesh_settings["meshCoef"]
            element_size = round(dimension / mesh_coef, 3)
            sizing.ElementSize = Quantity(element_size, "mm")
        
        method = mesh.AddAutomaticMethod()
        method.Location = ns
        
        mesh_method = getattr(MethodType, mesh_settings["meshMethod"])
        element_order = getattr(ElementOrder, mesh_settings["elementOrder"])
        
        method.Method = mesh_method
        method.ElementOrder = element_order
        
        if mesh_method == MethodType.MultiZone:
            method.SurfaceMeshMethod = 1
        elif mesh_method == MethodType.Sweep:
            method.Algorithm = MeshMethodAlgorithm.Axisymmetric
        
        method.RenameBasedOnDefinition()