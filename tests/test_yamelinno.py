"""
This module is used to validate the main script.
"""
# pylint: disable=missing-docstring
import unittest

from yamelinno import main

class TestMain(unittest.TestCase):
    def test_main(self):
        with self.assertRaises(SystemExit):
            main(['--version'])

    def test_main_invalid(self):
        with self.assertRaises(SystemExit):
            main(['--invalid'])

    def test_main_invalid_input(self):
        with self.assertRaises(SystemExit):
            main(['--schema', 'tests/data/schema.yml', 'tests/data/invalid.yml'])

if __name__ == '__main__':
    unittest.main()
