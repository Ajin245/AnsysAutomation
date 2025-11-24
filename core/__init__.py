# -*- coding: utf-8 -*-
"""
Core modules for ANSYS Automation
"""

from .structure_detector import StructureDetector
from .execution_manager import ExecutionManager
from .named_selection_manager import NamedSelectionManager

__all__ = [
    'StructureDetector',
    'ExecutionManager', 
    'NamedSelectionManager'
]