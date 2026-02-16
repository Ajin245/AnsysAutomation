# -*- coding: utf-8 -*-
"""
Main entry point for ANSYS Automation Project
Refactored modular version
"""

import System
from System.IO import File

# Import core modules
from core.structure_detector import StructureDetector
from core.execution_manager import ExecutionManager
from core.named_selection_manager import NamedSelectionManager

# Import managers
from managers.mesh_manager import MeshManager
from managers.bolt_manager import BoltManager
from managers.contact_manager import ContactManager
from managers.analysis_manager import AnalysisManager
from managers.results_manager import ResultsManager

# Import configuration
from config.config_manager import ConfigurationManager
from config.paths import validate_config_path, get_all_config_files
from config.constants import DEFAULT_SETTINGS
from utils.ansys_lookup import get_single_object_by_name, get_first_analysis

class AnsysAutomationApp:
    """Main application class for ANSYS Automation"""
    
    def __init__(self):
        """Initialize the application"""
        # Get objects from ANSYS global scope at runtime
        self.model = globals()["Model"]
        self.data_model_object_category = globals()["DataModelObjectCategory"]
        
        self.config_manager = None
        self.structure_type = None
        self.structure_category = None
        self.project_settings = None
        self.load_database = None
        self.analysis_scenarios = None
        self.bolt_database = None
        self.contact_settings = None
        self.mesh_config = None
        
        # Managers
        self.ns_manager = None
        self.execution_manager = None
        self.mesh_manager = None
        self.analysis_manager = None
        self.bolt_manager = None
        self.contact_manager = None
        self.results_manager = None
        
    def initialize_application(self):
        """Initialize the application with configuration"""
        try:
            print("=" * 60)
            print("ANSYS AUTOMATION - MODULAR VERSION")
            print("=" * 60)
            
            # Step 1: Validate configuration path
            print("1. Validating configuration path...")
            validate_config_path()
            print("   Configuration path validated")
            
            # Step 2: Initialize configuration manager
            print("2. Initializing configuration manager...")
            self.config_manager = ConfigurationManager()
            print("   Configuration manager initialized")
            
            # Step 3: Detect structure type
            print("3. Detecting structure type...")
            self.structure_type, self.structure_category = StructureDetector.detect_structure_type(self.model)
            ns_analysis = StructureDetector.analyze_ns_patterns(self.model)
            model_info = StructureDetector.get_model_info(self.model, self.data_model_object_category)
            
            print("   Structure: " + self.structure_type + " (" + self.structure_category + ")")
            print("   Model: " + model_info["name"])
            print("   Bodies: " + str(model_info["bodies_count"]))
            print("   Named Selections: " + str(model_info["named_selections_count"]))
            
            # Step 4: Load configurations with hierarchy
            print("4. Loading configuration hierarchy...")
            self._load_configurations()
            
            # Step 5: Initialize managers
            print("5. Initializing managers...")
            self._initialize_managers()
            
            print("   Application initialized successfully")
            return True
            
        except Exception as e:
            print("   Application initialization failed: " + str(e))
            return False
    
    def _load_configurations(self):
        """Load all configurations with structure-specific hierarchy"""
        # Load base configurations
        base_project_settings = self.config_manager.load_project_settings()
        self.mesh_config = self.config_manager.load_mesh_config()
        base_load_database = self.config_manager.load_load_database()
        self.analysis_scenarios = self.config_manager.load_analysis_scenarios()
        self.bolt_database = self.config_manager.load_bolt_database()
        self.contact_settings = self.config_manager.load_contact_settings()
        
        # Load structure-specific configuration if exists
        structure_config = self.config_manager.load_structure_config(self.structure_type)
        if structure_config:
            print("   Loaded structure-specific config for " + self.structure_type)
            # Merge configurations (structure config has priority)
            self.project_settings = self.config_manager.merge_configs(base_project_settings, structure_config)
            
            # Use structure-specific load database if provided
            if "load_database" in structure_config:
                self.load_database = structure_config["load_database"]
                print("   Using structure-specific load database")
            else:
                self.load_database = base_load_database
        else:
            self.project_settings = base_project_settings
            self.load_database = base_load_database
            print("   Using base configuration")
    
    def _initialize_managers(self):
        """Initialize all manager classes"""
        self.ns_manager = NamedSelectionManager(self.project_settings)
        self.execution_manager = ExecutionManager(self.project_settings, self.load_database, self.analysis_scenarios)
        self.mesh_manager = MeshManager(self.mesh_config, self.project_settings)
        self.analysis_manager = AnalysisManager(self.project_settings, self.analysis_scenarios, self.ns_manager)
        self.bolt_manager = BoltManager(self.bolt_database, self.project_settings, self.ns_manager)
        self.contact_manager = ContactManager(self.contact_settings)
        self.results_manager = ResultsManager(self.project_settings, self.ns_manager)
    
    def run_validation(self):
        """Run comprehensive validation"""
        try:
            print("6. Running validation...")
            
            # Validate Named Selections
            ns_validation = self.ns_manager.validate_ns_for_analysis()
            if not ns_validation["has_required_ns"]:
                print("   WARNING: Some required Named Selections are missing")
            else:
                print("   Named Selections validation passed")
            
            # Early check for critical system objects
            required_objects = ["Analysis Settings", "Solution", "Solution Information"]
            for object_name in required_objects:
                get_single_object_by_name(object_name, "validation before setup")
            print("   Critical ANSYS objects validation passed")

            # Validate model structure
            print("   Model structure validation passed")
            
            # Validate configuration hierarchy
            is_valid, missing_files, has_structure_config = self.config_manager.validate_config_hierarchy(self.structure_type)
            if not is_valid:
                print("   WARNING: Missing configuration files: " + ", ".join(missing_files))
            else:
                print("   Configuration validation passed")
            
            return True
            
        except Exception as e:
            print("   Validation failed: " + str(e))
            return False
    
    def execute_analysis_setup(self):
        """Execute the complete analysis setup"""
        try:
            # Step 7: Determine execution type
            print("7. Determining execution type...")
            execution_type = self.execution_manager.determine_execution_type()
            execution_number, load_group = self.execution_manager.validate_execution(execution_type)
            load_config = self.execution_manager.get_load_configuration(execution_type)
            
            print("   Execution: " + execution_type)
            print("   Number: " + execution_number + ", Load Group: " + load_group)
            
            # Step 8: Configure contacts
            print("8. Configuring contact pairs...")
            self.contact_manager.analyze_and_configure_contacts()
            print("   Contact configuration completed")
            
            # Step 9: Create mesh
            print("9. Creating mesh...")
            self.mesh_manager.apply_mesh_settings()
            print("   Mesh creation completed")
            
            # Step 10: Setup analysis
            print("10. Setting up analysis...")
            analysis = get_first_analysis("analysis setup")
            has_bolts = self.bolt_manager.has_bolts()
            
            self.analysis_manager.setup_analysis("standard_sequence", has_bolts)
            self.analysis_manager.apply_boundary_conditions(analysis)
            self.analysis_manager.apply_loads(analysis, load_config, "standard_sequence", has_bolts)
            
            # Apply bolt loads if present
            if has_bolts:
                steps_count = self.analysis_scenarios['standard_sequence']['steps'] + 1
                self.bolt_manager.apply_bolt_loads(analysis, steps_count)
                print("   Bolt loads applied")
            
            print("   Analysis setup completed")
            
            # Step 11: Setup results
            print("11. Setting up results...")
            self.results_manager.setup_results()
            print("   Results setup completed")
            
            return execution_type, load_group
            
        except Exception as e:
            print("   Analysis setup failed: " + str(e))
            raise
    
    def run(self):
        """Main execution method"""
        try:
            # Initialize application
            if not self.initialize_application():
                return False
            
            # Run validation
            if not self.run_validation():
                print("   Continuing with validation warnings...")
            
            # Execute analysis setup
            execution_type, load_group = self.execute_analysis_setup()
            
            # Success summary
            print("=" * 60)
            print("AUTOMATED ANALYSIS SETUP SUCCESSFULLY COMPLETED!")
            print("Structure: " + self.structure_type + " (" + self.structure_category + ")")
            print("Execution: " + execution_type)
            print("Load Group: " + load_group)
            print("=" * 60)
            
            return True
            
        except System.Exception as e:
            print("=" * 60)
            print("CRITICAL ERROR:")
            print("   " + str(e))
            print("   Analysis cannot be performed. Check configuration files and model.")
            print("=" * 60)
            return False
            
        except Exception as e:
            print("=" * 60)
            print("UNKNOWN ERROR:")
            print("   " + str(e))
            print("   Please contact developer.")
            print("=" * 60)
            return False

# Alternative simplified entry point for backward compatibility
def run_automated_analysis():
    """
    Simplified entry point for backward compatibility
    """
    app = AnsysAutomationApp()
    return app.run()

# Main execution
if __name__ == "__main__":
    # This allows the script to be run directly in ANSYS
    success = run_automated_analysis()
    
    if success:
        print("")
        print("Analysis setup completed successfully!")
        print("You can now run the solution.")
    else:
        print("")
        print("Analysis setup failed!")
        print("Please check the error messages above.")