# -*- coding: utf-8 -*-
"""
Pattern matching utilities for ANSYS Automation
"""

import re

def simple_pattern_match(name, pattern):
    """
    Simple pattern matching without fnmatch for IronPython compatibility
    
    Args:
        name (str): String to match against
        pattern (str): Pattern with wildcards (*)
        
    Returns:
        bool: True if name matches pattern
    """
    if not pattern or not name:
        return False
        
    if '*' in pattern:
        parts = pattern.split('*', 1)
        if len(parts) == 2:
            prefix, suffix = parts
            return name.startswith(prefix) and name.endswith(suffix)
        else:
            return pattern.replace('*', '') in name
    else:
        return name == pattern

def extract_number_from_name(entity_name):
    """
    Extract number from entity name using regex
    
    Args:
        entity_name (str): Name like "mbolt12" or "opora_15"
        
    Returns:
        tuple: (base_name, number) or None if no number found
    """
    match = re.match(r"^(.*?)([+-]?\d*\.\d+|\d+\.?\d*)$", entity_name)
    if match:
        return match.group(1), float(match.group(2))
    return None

def match_any_pattern(name, patterns):
    """
    Check if name matches any pattern in the list
    
    Args:
        name (str): String to check
        patterns (list): List of patterns
        
    Returns:
        bool: True if matches any pattern
    """
    return any(simple_pattern_match(name, pattern) for pattern in patterns)

def find_matching_names(names, pattern):
    """
    Find all names matching the pattern
    
    Args:
        names (list): List of names to search
        pattern (str): Pattern to match
        
    Returns:
        list: List of matching names
    """
    return [name for name in names if simple_pattern_match(name, pattern)]