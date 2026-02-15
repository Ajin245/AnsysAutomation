# -*- coding: utf-8 -*-
import importlib
import os
import sys
import tempfile
import types
import unittest


class JsonParserTests(unittest.TestCase):
    def setUp(self):
        self._orig_system = sys.modules.get('System')
        system_module = types.ModuleType('System')
        system_io_module = types.ModuleType('System.IO')

        class _File:
            @staticmethod
            def Exists(path):
                return os.path.exists(path)

        class _StreamReader:
            def __init__(self, path):
                self._path = path
                self._handle = None

            def __enter__(self):
                self._handle = open(self._path, 'r', encoding='utf-8')
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self._handle is not None:
                    self._handle.close()

            def ReadToEnd(self):
                return self._handle.read()

        class _IO:
            File = _File

        system_io_module.StreamReader = _StreamReader
        system_io_module.File = _File
        system_module.IO = _IO
        system_module.Exception = Exception

        sys.modules['System'] = system_module
        sys.modules['System.IO'] = system_io_module

        if 'utils.json_parser' in sys.modules:
            del sys.modules['utils.json_parser']
        self.json_parser = importlib.import_module('utils.json_parser')

    def tearDown(self):
        if self._orig_system is not None:
            sys.modules['System'] = self._orig_system
        elif 'System' in sys.modules:
            del sys.modules['System']

        if 'System.IO' in sys.modules:
            del sys.modules['System.IO']

    def test_remove_comments_preserves_string_content(self):
        raw = '{\n  "text": "a b, c: d // not comment",\n  // remove\n  "block": "x/*keep*/y",\n  /* remove */\n  "n": 1\n}'
        cleaned = self.json_parser._remove_json_comments(raw)
        parsed = self.json_parser.parse_json(cleaned)

        self.assertEqual(parsed['text'], 'a b, c: d // not comment')
        self.assertEqual(parsed['block'], 'x/*keep*/y')
        self.assertEqual(parsed['n'], 1)

    def test_load_json_file_with_comments_and_complex_string(self):
        content = '{\n  "msg": "value with spaces, comma, and colon: ok",\n  "arr": [1, 2, 3], // trailing comment\n  /* block comment */\n  "obj": {"k": "v"}\n}'
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as tmp:
            tmp.write(content)
            path = tmp.name

        try:
            parsed = self.json_parser.load_json_file(path)
            self.assertEqual(parsed['msg'], 'value with spaces, comma, and colon: ok')
            self.assertEqual(parsed['arr'], [1, 2, 3])
            self.assertEqual(parsed['obj']['k'], 'v')
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
