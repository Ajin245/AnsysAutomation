# -*- coding: utf-8 -*-
"""
JSON parser utilities for IronPython compatibility
"""

import re
import System
from System.IO import StreamReader

def parse_json(json_string):
    """
    Simple JSON parser for IronPython compatibility
    
    Args:
        json_string (str): JSON string to parse
        
    Returns:
        object: Parsed Python object
    """
    if not json_string:
        return None
        
    json_string = json_string.strip()
    
    if json_string.startswith('{') and json_string.endswith('}'):
        return parse_json_object(json_string[1:-1])
    elif json_string.startswith('[') and json_string.endswith(']'):
        return parse_json_array(json_string[1:-1])
    elif json_string.startswith('"') and json_string.endswith('"'):
        return json_string[1:-1]
    elif json_string.lower() == 'true':
        return True
    elif json_string.lower() == 'false':
        return False
    elif json_string.lower() == 'null':
        return None
    else:
        try:
            if '.' in json_string:
                return float(json_string)
            else:
                return int(json_string)
        except:
            return json_string

def parse_json_object(obj_string):
    """
    Parse JSON object string into dictionary
    
    Args:
        obj_string (str): JSON object content
        
    Returns:
        dict: Parsed dictionary
    """
    result = {}
    if not obj_string:
        return result
        
    pairs = _split_json_pairs(obj_string)
    for pair in pairs:
        key, value = pair.split(':', 1)
        key = key.strip().strip('"')
        result[key] = parse_json(value.strip())
    return result

def parse_json_array(array_string):
    """
    Parse JSON array string into list
    
    Args:
        array_string (str): JSON array content
        
    Returns:
        list: Parsed list
    """
    result = []
    if not array_string:
        return result
        
    items = _split_json_items(array_string)
    for item in items:
        result.append(parse_json(item.strip()))
    return result

def _split_json_pairs(obj_string):
    """
    Split object string into key-value pairs
    
    Args:
        obj_string (str): JSON object content
        
    Returns:
        list: List of key-value pair strings
    """
    pairs = []
    depth = 0
    start = 0
    
    for i, char in enumerate(obj_string):
        if char == '{' or char == '[':
            depth += 1
        elif char == '}' or char == ']':
            depth -= 1
        elif char == ',' and depth == 0:
            pairs.append(obj_string[start:i])
            start = i + 1
    
    if start < len(obj_string):
        pairs.append(obj_string[start:])
    
    return pairs

def _split_json_items(array_string):
    """
    Split array string into items
    
    Args:
        array_string (str): JSON array content
        
    Returns:
        list: List of item strings
    """
    items = []
    depth = 0
    start = 0
    
    for i, char in enumerate(array_string):
        if char == '{' or char == '[':
            depth += 1
        elif char == '}' or char == ']':
            depth -= 1
        elif char == ',' and depth == 0:
            items.append(array_string[start:i])
            start = i + 1
    
    if start < len(array_string):
        items.append(array_string[start:])
    
    return items

def load_json_file(file_path):
    """
    Load and parse JSON file with comments support
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        object: Parsed JSON content
        
    Raises:
        System.Exception: If file not found or parsing error
    """
    if not System.IO.File.Exists(file_path):
        raise System.Exception("Configuration file not found: " + file_path)
    
    try:
        with StreamReader(file_path) as stream:
            json_string = stream.ReadToEnd()
        
        # Remove comments and whitespace
        json_string = re.sub(r'//.*?\n', '', json_string)
        json_string = re.sub(r'/\*[\s\S]*?\*/', '', json_string)
        json_string = re.sub(r'\s+', '', json_string)
        
        return parse_json(json_string)
        
    except Exception as e:
        raise System.Exception("Error loading " + file_path + ": " + str(e))