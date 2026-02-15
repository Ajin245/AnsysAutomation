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
        self.validation_errors = []
    
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
    
    def validate_configuration(self):
        """Validate boundary conditions and loads configuration"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if using new configuration format
        has_bc_config = "boundary_conditions_config" in self.project_settings
        has_loads_config = "loads_config" in self.project_settings
        
        if has_bc_config:
            bc_errors, bc_warnings = self._validate_boundary_conditions_config()
            validation_results["errors"].extend(bc_errors)
            validation_results["warnings"].extend(bc_warnings)
        
        if has_loads_config:
            load_errors, load_warnings = self._validate_loads_config()
            validation_results["errors"].extend(load_errors)
            validation_results["warnings"].extend(load_warnings)
        
        validation_results["is_valid"] = len(validation_results["errors"]) == 0
        
        return validation_results
    
    def _validate_boundary_conditions_config(self):
        """Validate boundary conditions configuration"""
        errors = []
        warnings = []
        
        bc_config_list = self.project_settings.get("boundary_conditions_config", [])
        
        if not bc_config_list:
            warnings.append("boundary_conditions_config is empty")
            return errors, warnings
        
        supported_types = [
            "fixed_support", "rotation_constraint", "displacement",
            "remote_displacement", "frictionless_support", "compression_only_support"
        ]
        
        for idx, bc_config in enumerate(bc_config_list):
            # Check required fields
            if "type" not in bc_config:
                errors.append(f"BC config [{idx}]: missing 'type' field")
                continue
            
            bc_type = bc_config["type"]
            
            # Check if type is supported
            if bc_type not in supported_types:
                errors.append(f"BC config [{idx}]: unsupported type '{bc_type}'")
                continue
            
            # Check for named_selection
            if "named_selection" not in bc_config:
                errors.append(f"BC config [{idx}]: missing 'named_selection' field")
                continue
            
            ns_name = bc_config["named_selection"]
            
            # Validate named selection exists
            ns = self.ns_manager.get_ns_by_name(ns_name)
            if not ns:
                warnings.append(f"BC config [{idx}]: named selection '{ns_name}' not found")
            
            # Type-specific validation
            if bc_type in ["displacement", "remote_displacement"]:
                if "components" in bc_config:
                    components = bc_config["components"]
                    if not isinstance(components, dict):
                        errors.append(f"BC config [{idx}]: 'components' must be a dictionary")
        
        return errors, warnings
    
    def _validate_loads_config(self):
        """Validate loads configuration"""
        errors = []
        warnings = []
        
        loads_config_list = self.project_settings.get("loads_config", [])
        
        if not loads_config_list:
            warnings.append("loads_config is empty")
            return errors, warnings
        
        supported_types = [
            "force", "moment", "pressure", "remote_force",
            "bearing_load", "bolt_pretension", "temperature"
        ]
        
        for idx, load_config in enumerate(loads_config_list):
            # Check required fields
            if "type" not in load_config:
                errors.append(f"Load config [{idx}]: missing 'type' field")
                continue
            
            load_type = load_config["type"]
            
            # Check if type is supported
            if load_type not in supported_types:
                errors.append(f"Load config [{idx}]: unsupported type '{load_type}'")
                continue
            
            # Bolt pretension doesn't require named_selection (automatic)
            if load_type == "bolt_pretension":
                continue
            
            # Check for named_selection for other load types
            if "named_selection" not in load_config:
                errors.append(f"Load config [{idx}]: missing 'named_selection' field")
                continue
            
            ns_name = load_config["named_selection"]
            
            # Validate named selection exists
            ns = self.ns_manager.get_ns_by_name(ns_name)
            if not ns:
                warnings.append(f"Load config [{idx}]: named selection '{ns_name}' not found")
            
            # Check use_database flag
            use_database = load_config.get("use_database", False)
            
            # If not using database, check for static values
            if not use_database:
                if load_type == "force" and "components" not in load_config:
                    errors.append(f"Load config [{idx}]: force load requires 'components' when not using database")
                elif load_type == "moment" and "components" not in load_config:
                    errors.append(f"Load config [{idx}]: moment load requires 'components' when not using database")
                elif load_type in ["pressure", "temperature"] and "value" not in load_config:
                    errors.append(f"Load config [{idx}]: {load_type} requires 'value' when not using database")
        
        return errors, warnings
    
    def apply_boundary_conditions(self, analysis):
        """Apply all types of boundary conditions"""
        # Check if structure-specific boundary conditions config exists
        if "boundary_conditions_config" in self.project_settings:
            self._apply_boundary_conditions_from_config(analysis)
        else:
            # Fallback to legacy method
            self._apply_boundary_conditions_legacy(analysis)
    
    def _apply_boundary_conditions_legacy(self, analysis):
        """Apply boundary conditions using legacy configuration format"""
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
    
    def _apply_boundary_conditions_from_config(self, analysis):
        """Apply boundary conditions from structure-specific configuration"""
        bc_config_list = self.project_settings["boundary_conditions_config"]
        
        print("   Applying boundary conditions from structure-specific config...")
        
        for bc_config in bc_config_list:
            bc_type = bc_config.get("type")
            ns_name = bc_config.get("named_selection")
            
            if not bc_type:
                self.validation_errors.append("Boundary condition missing 'type' field")
                continue
            
            # Get named selection
            ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
            
            if not ns and ns_name:
                error_msg = f"Named selection '{ns_name}' not found for BC type '{bc_type}'"
                self.validation_errors.append(error_msg)
                print(f"   WARNING: {error_msg}")
                continue
            
            # Apply boundary condition based on type
            try:
                if bc_type == "fixed_support":
                    self._apply_fixed_support(analysis, ns)
                    print(f"   Applied Fixed Support at '{ns_name}'")
                    
                elif bc_type == "rotation_constraint":
                    self._apply_rotation_constraint(analysis, ns)
                    print(f"   Applied Rotation Constraint at '{ns_name}'")
                    
                elif bc_type == "displacement":
                    components = bc_config.get("components", {})
                    self._apply_displacement(analysis, ns, components)
                    print(f"   Applied Displacement at '{ns_name}'")
                    
                elif bc_type == "remote_displacement":
                    components = bc_config.get("components", {})
                    self._apply_remote_displacement(analysis, ns, components)
                    print(f"   Applied Remote Displacement at '{ns_name}'")
                    
                elif bc_type == "frictionless_support":
                    self._apply_frictionless_support(analysis, ns)
                    print(f"   Applied Frictionless Support at '{ns_name}'")
                    
                elif bc_type == "compression_only_support":
                    self._apply_compression_only_support(analysis, ns)
                    print(f"   Applied Compression Only Support at '{ns_name}'")
                    
                else:
                    error_msg = f"Unknown boundary condition type: {bc_type}"
                    self.validation_errors.append(error_msg)
                    print(f"   WARNING: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Failed to apply BC type '{bc_type}': {str(e)}"
                self.validation_errors.append(error_msg)
                print(f"   ERROR: {error_msg}")
    
    def _apply_fixed_support(self, analysis, ns):
        """Apply fixed support boundary condition"""
        fixed_support = analysis.AddFixedSupport()
        fixed_support.Location = ns
    
    def _apply_rotation_constraint(self, analysis, ns):
        """Apply rotation constraint (Remote Displacement with RotX=RotY=RotZ=0)"""
        remote_disp = analysis.AddRemoteDisplacement()
        remote_disp.Location = ns
        # Set rotation constraints to 0
        remote_disp.RotationX = Quantity(0, "deg")
        remote_disp.RotationY = Quantity(0, "deg")
        remote_disp.RotationZ = Quantity(0, "deg")
    
    def _apply_displacement(self, analysis, ns, components):
        """Apply displacement boundary condition with components"""
        displacement = analysis.AddDisplacement()
        displacement.Location = ns
        if components:
            if "x" in components:
                displacement.XComponent = Quantity(components["x"], "mm")
            if "y" in components:
                displacement.YComponent = Quantity(components["y"], "mm")
            if "z" in components:
                displacement.ZComponent = Quantity(components["z"], "mm")
    
    def _apply_remote_displacement(self, analysis, ns, components):
        """Apply remote displacement with custom components"""
        remote_disp = analysis.AddRemoteDisplacement()
        remote_disp.Location = ns
        if components:
            if "x" in components:
                remote_disp.XComponent = Quantity(components["x"], "mm")
            if "y" in components:
                remote_disp.YComponent = Quantity(components["y"], "mm")
            if "z" in components:
                remote_disp.ZComponent = Quantity(components["z"], "mm")
            if "rotx" in components:
                remote_disp.RotationX = Quantity(components["rotx"], "deg")
            if "roty" in components:
                remote_disp.RotationY = Quantity(components["roty"], "deg")
            if "rotz" in components:
                remote_disp.RotationZ = Quantity(components["rotz"], "deg")
    
    def _apply_frictionless_support(self, analysis, ns):
        """Apply frictionless support boundary condition"""
        frictionless = analysis.AddFrictionlessSupport()
        frictionless.Location = ns
    
    def _apply_compression_only_support(self, analysis, ns):
        """Apply compression only support boundary condition"""
        compression_only = analysis.AddCompressionOnlySupport()
        compression_only.Location = ns
    
    def apply_loads(self, analysis, load_config, scenario_name, has_bolts=False):
        """Apply loads with proper step configuration"""
        # Check if structure-specific loads config exists
        if "loads_config" in self.project_settings:
            self._apply_loads_from_config(analysis, load_config, scenario_name, has_bolts)
        else:
            # Fallback to legacy method
            self._apply_loads_legacy(analysis, load_config, scenario_name, has_bolts)
    
    def _build_load_timeline(self, scenario_name, has_bolts=False):
        """Build and validate time steps and load factors for scenario."""
        scenario = self.analysis_scenarios[scenario_name]
        steps = scenario["steps"]
        load_factors = scenario.get("load_factors")

        if load_factors is None:
            raise System.Exception("Scenario has no 'load_factors': " + str(scenario_name))

        expected_factors = steps
        if len(load_factors) != expected_factors:
            raise System.Exception(
                "Scenario '{0}': load_factors length ({1}) must be equal to steps ({2})".format(
                    scenario_name, len(load_factors), expected_factors
                )
            )

        if has_bolts:
            time_steps = [Quantity(i, "s") for i in range(steps + 1)]
            load_factors_shifted = [0] + load_factors
        else:
            time_steps = [Quantity(i, "s") for i in range(steps)]
            load_factors_shifted = load_factors

        if len(time_steps) != len(load_factors_shifted):
            raise System.Exception(
                "Scenario '{0}': mismatch between time steps ({1}) and load factors ({2}) after bolt-step shift".format(
                    scenario_name, len(time_steps), len(load_factors_shifted)
                )
            )

        return time_steps, load_factors_shifted

    def _apply_loads_legacy(self, analysis, load_config, scenario_name, has_bolts=False):
        """Apply loads using legacy configuration format"""
        load_settings = self.project_settings["loads"]
        time_steps, load_factors_shifted = self._build_load_timeline(scenario_name, has_bolts)
        
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
    
    def _apply_loads_from_config(self, analysis, load_config, scenario_name, has_bolts=False):
        """Apply loads from structure-specific configuration"""
        loads_config_list = self.project_settings["loads_config"]

        print("   Applying loads from structure-specific config...")

        time_steps, load_factors_shifted = self._build_load_timeline(scenario_name, has_bolts)
        
        for load_def in loads_config_list:
            load_type = load_def.get("type")
            
            if not load_type:
                self.validation_errors.append("Load definition missing 'type' field")
                continue
            
            try:
                if load_type == "force":
                    self._apply_force_load(analysis, load_def, load_config, time_steps, load_factors_shifted)
                    
                elif load_type == "moment":
                    self._apply_moment_load(analysis, load_def, load_config, time_steps, load_factors_shifted)
                    
                elif load_type == "pressure":
                    self._apply_pressure_load(analysis, load_def, load_config, time_steps, load_factors_shifted)
                    
                elif load_type == "remote_force":
                    self._apply_remote_force_load(analysis, load_def, load_config, time_steps, load_factors_shifted)
                    
                elif load_type == "bearing_load":
                    self._apply_bearing_load(analysis, load_def, load_config, time_steps, load_factors_shifted)
                    
                elif load_type == "bolt_pretension":
                    # Bolt pretension is handled separately by BoltManager
                    print("   Bolt pretension will be applied by BoltManager")
                    
                elif load_type == "temperature":
                    self._apply_temperature_load(analysis, load_def, time_steps, load_factors_shifted)
                    
                else:
                    error_msg = f"Unknown load type: {load_type}"
                    self.validation_errors.append(error_msg)
                    print(f"   WARNING: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Failed to apply load type '{load_type}': {str(e)}"
                self.validation_errors.append(error_msg)
                print(f"   ERROR: {error_msg}")
    
    def _apply_force_load(self, analysis, load_def, load_config, time_steps, load_factors):
        """Apply force load with X, Y, Z components"""
        ns_name = load_def.get("named_selection")
        use_database = load_def.get("use_database", False)
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        force = analysis.AddForce()
        force.Location = ns
        force.DefineBy = LoadDefineBy.Components
        
        if use_database:
            # Get force values from load_config (from database)
            if "forces" in load_config:
                for comp in ["X", "Y", "Z"]:
                    comp_lower = comp.lower()
                    force_value = load_config["forces"].get("f" + comp_lower, 0)
                    if force_value != 0:
                        comp_obj = getattr(force, comp + "Component")
                        comp_obj.Inputs[0].DiscreteValues = time_steps
                        values = [Quantity(force_value * factor, "N") for factor in load_factors]
                        comp_obj.Output.DiscreteValues = values
                print(f"   Applied Force at '{ns_name}' (from database)")
            else:
                raise Exception("Force values not found in load_config")
        else:
            # Use static values from configuration
            components = load_def.get("components", {})
            for comp in ["X", "Y", "Z"]:
                comp_lower = comp.lower()
                if "f" + comp_lower in components:
                    force_value = components["f" + comp_lower]
                    comp_obj = getattr(force, comp + "Component")
                    comp_obj.Inputs[0].DiscreteValues = time_steps
                    values = [Quantity(force_value * factor, "N") for factor in load_factors]
                    comp_obj.Output.DiscreteValues = values
            print(f"   Applied Force at '{ns_name}' (static values)")
    
    def _apply_moment_load(self, analysis, load_def, load_config, time_steps, load_factors):
        """Apply moment load"""
        ns_name = load_def.get("named_selection")
        use_database = load_def.get("use_database", False)
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        moment = analysis.AddMoment()
        moment.Location = ns
        moment.DefineBy = LoadDefineBy.Components
        
        if use_database:
            if "moments" in load_config:
                for comp in ["X", "Y", "Z"]:
                    comp_lower = comp.lower()
                    moment_value = load_config["moments"].get("m" + comp_lower, 0)
                    if moment_value != 0:
                        comp_obj = getattr(moment, comp + "Component")
                        comp_obj.Inputs[0].DiscreteValues = time_steps
                        values = [Quantity(moment_value * factor, "N*mm") for factor in load_factors]
                        comp_obj.Output.DiscreteValues = values
                print(f"   Applied Moment at '{ns_name}' (from database)")
            else:
                raise Exception("Moment values not found in load_config")
        else:
            components = load_def.get("components", {})
            for comp in ["X", "Y", "Z"]:
                comp_lower = comp.lower()
                if "m" + comp_lower in components:
                    moment_value = components["m" + comp_lower]
                    comp_obj = getattr(moment, comp + "Component")
                    comp_obj.Inputs[0].DiscreteValues = time_steps
                    values = [Quantity(moment_value * factor, "N*mm") for factor in load_factors]
                    comp_obj.Output.DiscreteValues = values
            print(f"   Applied Moment at '{ns_name}' (static values)")
    
    def _apply_pressure_load(self, analysis, load_def, load_config, time_steps, load_factors):
        """Apply pressure load"""
        ns_name = load_def.get("named_selection")
        use_database = load_def.get("use_database", False)
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        pressure = analysis.AddPressure()
        pressure.Location = ns
        
        if use_database:
            if "pressure" in load_config:
                pressure_value = load_config["pressure"]
                pressure.Magnitude.Output.DiscreteValues = [
                    Quantity(pressure_value * factor, "MPa") for factor in load_factors
                ]
                print(f"   Applied Pressure at '{ns_name}' (from database)")
            else:
                raise Exception("Pressure value not found in load_config")
        else:
            pressure_value = load_def.get("value", 0)
            pressure.Magnitude.Output.DiscreteValues = [
                Quantity(pressure_value * factor, "MPa") for factor in load_factors
            ]
            print(f"   Applied Pressure at '{ns_name}' (static value)")
    
    def _apply_remote_force_load(self, analysis, load_def, load_config, time_steps, load_factors):
        """Apply remote force load"""
        ns_name = load_def.get("named_selection")
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        remote_force = analysis.AddRemoteForce()
        remote_force.Location = ns
        print(f"   Applied Remote Force at '{ns_name}'")
    
    def _apply_bearing_load(self, analysis, load_def, load_config, time_steps, load_factors):
        """Apply bearing load"""
        ns_name = load_def.get("named_selection")
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        bearing = analysis.AddBearing()
        bearing.Location = ns
        print(f"   Applied Bearing Load at '{ns_name}'")
    
    def _apply_temperature_load(self, analysis, load_def, time_steps, load_factors):
        """Apply temperature load"""
        ns_name = load_def.get("named_selection")
        value = load_def.get("value", 0)
        
        ns = self.ns_manager.get_ns_by_name(ns_name) if ns_name else None
        if not ns:
            raise Exception(f"Named selection '{ns_name}' not found")
        
        temperature = analysis.AddTemperature()
        temperature.Location = ns
        temperature.Magnitude = Quantity(value, "C")
        print(f"   Applied Temperature at '{ns_name}'")
    
    def get_validation_errors(self):
        """Get list of validation errors encountered during configuration"""
        return self.validation_errors
    
    def clear_validation_errors(self):
        """Clear validation errors list"""
        self.validation_errors = []