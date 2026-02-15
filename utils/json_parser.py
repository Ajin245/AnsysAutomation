# -*- coding: utf-8 -*-
"""
JSON parser utilities for IronPython compatibility
"""

import json
import System
from System.IO import StreamReader


def _remove_json_comments(json_string):
    """
    Remove // and /* ... */ comments while preserving content inside JSON strings.

    Args:
        json_string (str): Raw JSON content

    Returns:
        str: JSON content with comments removed
    """
    result = []
    in_string = False
    escaped = False
    i = 0
    length = len(json_string)

    while i < length:
        char = json_string[i]

        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue

        if char == '"':
            in_string = True
            result.append(char)
            i += 1
            continue

        if char == '/' and i + 1 < length:
            next_char = json_string[i + 1]

            # Line comment: // ...\n
            if next_char == '/':
                i += 2
                while i < length and json_string[i] != '\n':
                    i += 1
                continue

            # Block comment: /* ... */
            if next_char == '*':
                i += 2
                while i + 1 < length and not (json_string[i] == '*' and json_string[i + 1] == '/'):
                    i += 1
                i += 2
                continue

        result.append(char)
        i += 1

    return ''.join(result)


def parse_json(json_string):
    """
    Parse JSON string using standard deserializer.

    Args:
        json_string (str): JSON string to parse

    Returns:
        object: Parsed Python object
    """
    if json_string is None:
        return None

    return json.loads(json_string)


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

        json_string = _remove_json_comments(json_string)
        return parse_json(json_string)

    except Exception as e:
        raise System.Exception("Error loading " + file_path + ": " + str(e))
