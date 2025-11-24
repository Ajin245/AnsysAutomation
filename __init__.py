# -*- coding: utf-8 -*-
"""
ANSYS Automation Project
Modular automation system for ANSYS Mechanical

Version: 2.0 (Modular)
"""

__version__ = "2.0.0"
__author__ = "Automation Team"
__description__ = "Modular automation system for ANSYS Mechanical analyses"

from .main import AnsysAutomationApp, run_automated_analysis

__all__ = ['AnsysAutomationApp', 'run_automated_analysis']