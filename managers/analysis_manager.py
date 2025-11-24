# -*- coding: utf-8 -*-
"""
Analysis setup manager for ANSYS Automation
"""

class AnalysisManager:
    """Analysis setup manager"""
    
    def __init__(self, project_settings, analysis_scenarios, named_selection_manager):
        self.project_settings = project_settings
        self.analysis_scenarios = analysis_scenarios
        self.ns_manager = named_selection_manager
    
    def setup_analysis(self, scenario_name="standard_sequence", has_bolts=False):
        """Setup analysis parameters"""
        analysis_settings = DataModel.GetObjectsByName("Analysis Settings")[0]
        scenario = self.analysis_scenarios[scenario_name]
        
        analysis_settings.NumberOfSteps = scenario["steps"]
        analysis_settings.LargeDeflection = True
        analysis_settings.NewtonRaphsonOption = NewtonRaphsonType.Unsymmetric
        analysis_settings.NodalForces = OutputControlsNodalForcesType.Yes
        analysis_settings.GeneralMiscellaneous = True
        analysis_settings.ContactMiscellaneous = True
        
        return analysis_settings
    
    def apply_boundary_conditions(self, analysis):
        """Apply all types of boundary conditions"""
        bc_settings = self.project_settings["boundary_conditions"]
        
        # Fixed support
        if bc_settings.get("fixed_support"):
            fixed_ns = self.ns_manager.get_ns_by_name(bc_settings["fixed_support"])
            if fixed_ns:
                fixed_support = analysis.AddFixedSupport()
                fixed_support.Location = fixed_ns
        
        # Displacement
        if bc_settings.get("displacement"):
            disp_ns = self.ns_manager.get_ns_by_name(bc_settings["displacement"])
            if disp_ns:
                displacement = analysis.AddDisplacement()
                displacement.Location = disp_ns
        
        # Remote Displacement
        if bc_settings.get("remote_displacement"):
            remote_disp_ns = self.ns_manager.get_ns_by_name(bc_settings["remote_displacement"])
            if remote_disp_ns:
                remote_disp = analysis.AddRemoteDisplacement()
                remote_disp.Location = remote_disp_ns
        
        # Remote Force
        if bc_settings.get("remote_force"):
            remote_force_ns = self.ns_manager.get_ns_by_name(bc_settings["remote_force"])
            if remote_force_ns:
                remote_force = analysis.AddRemoteForce()
                remote_force.Location = remote_force_ns
    
    def apply_loads(self, analysis, load_config, scenario_name, has_bolts=False):
        """Apply loads with proper step configuration"""
        load_settings = self.project_settings["loads"]
        scenario = self.analysis_scenarios[scenario_name]
        
        # Time steps configuration
        if has_bolts:
            time_steps = [Quantity(i, "s") for i in range(scenario["steps"] + 1)]
            load_factors_shifted = [0] + load_config["load_factors"]
        else:
            time_steps = [Quantity(i, "s") for i in range(scenario["steps"])]
            load_factors_shifted = load_config["load_factors"]
        
        # Force load
        if load_settings.get("force"):
            force_ns = self.ns_manager.get_ns_by_name(load_settings["force"])
            if force_ns:
                force = analysis.AddForce()
                force.Location = force_ns
                force.DefineBy = LoadDefineBy.Components
                
                for comp in ["X", "Y", "Z"]:
                    comp_lower = comp.lower()
                    force_value = load_config["forces"].get("f" + comp_lower, 0)
                    if force_value != 0:
                        comp_obj = getattr(force, comp + "Component")
                        comp_obj.Inputs[0].DiscreteValues = time_steps
                        values = [Quantity(force_value * factor, "N") for factor in load_factors_shifted]
                        comp_obj.Output.DiscreteValues = values
        
        # Moment load
        if load_settings.get("moment"):
            moment_ns = self.ns_manager.get_ns_by_name(load_settings["moment"])
            if moment_ns:
                moment = analysis.AddMoment()
                moment.Location = moment_ns
                moment.DefineBy = LoadDefineBy.Components
                
                for comp in ["X", "Y", "Z"]:
                    comp_lower = comp.lower()
                    moment_value = load_config["moments"].get("m" + comp_lower, 0)
                    if moment_value != 0:
                        comp_obj = getattr(moment, comp + "Component")
                        comp_obj.Inputs[0].DiscreteValues = time_steps
                        values = [Quantity(moment_value * factor, "N*mm") for factor in load_factors_shifted]
                        comp_obj.Output.DiscreteValues = values
        
        # Pressure load
        if load_settings.get("pressure"):
            pressure_ns = self.ns_manager.get_ns_by_name(load_settings["pressure"])
            if pressure_ns and load_config.get("pressure"):
                pressure = analysis.AddPressure()
                pressure.Location = pressure_ns
                pressure.Magnitude.Output.DiscreteValues = [
                    Quantity(load_config["pressure"] * factor, "MPa") 
                    for factor in load_factors_shifted
                ]