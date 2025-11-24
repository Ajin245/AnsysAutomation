# -*- coding: utf-8 -*-
"""
Results setup manager for ANSYS Automation
"""

from utils.pattern_matching import simple_pattern_match

class ResultsManager:
    """Results setup manager"""
    
    def __init__(self, project_settings, named_selection_manager):
        self.project_settings = project_settings
        self.ns_manager = named_selection_manager
    
    def setup_results(self):
        """Setup result sections"""
        solution_info = DataModel.GetObjectsByName("Solution Information")[0]
        solution_info.NewtonRaphsonResiduals = 4
        solution_info.IdentifyElementViolations = 4
        
        solution = solution_info.Parent
        solution.AddTotalDeformation()
        
        # Results for important NS
        important_keywords = self.project_settings.get("mesh_settings", {}).get("result_keywords", ["shov", "bolt", "opora", "truba", "osnovanie"])
        
        for ns in self.ns_manager.all_ns:
            if self._should_create_result_for_ns(ns.Name, important_keywords):
                self._create_stress_result(ns)
    
    def _should_create_result_for_ns(self, ns_name, important_keywords):
        """Determine if result should be created for Named Selection"""
        # Skip load and BC NS
        bc_settings = self.project_settings["boundary_conditions"]
        load_settings = self.project_settings["loads"]
        
        all_special_ns = []
        for ns_list in [bc_settings, load_settings]:
            for ns_name_val in ns_list.values():
                if ns_name_val:
                    all_special_ns.append(ns_name_val)
        
        bolt_pattern = self.project_settings["loads"].get("bolt_pattern", "gu_bolt*_f")
        if simple_pattern_match(ns_name, bolt_pattern):
            return False
                
        if ns_name in all_special_ns:
            return False
        
        return any(keyword in ns_name for keyword in important_keywords)
    
    def _create_stress_result(self, ns):
        """Create stress results for Named Selection"""
        solution = DataModel.GetObjectsByName("Solution")[0]
        
        if "shov" in ns.Name:
            shear_stress = solution.AddMaximumShearStress()
            shear_stress.Location = ns
            shear_stress.DisplayOption = ResultAveragingType.ElementalMean
        else:
            stress_intensity = solution.AddStressIntensity()
            stress_intensity.Location = ns