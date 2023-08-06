"""Test commands."""
import unittest

from pltk.flask_utils.commands import jsonize


class JsonizeTest(unittest.TestCase):
    """Test pltk.flask_utils.commands.jsonize()."""

    def test_empty_string(self):
        """Test if data is empty."""
        result = jsonize('')
        self.assertEqual(result, '{}')

    def test_list(self):
        """Test a simple list."""
        result = jsonize("a=[1,two,three]")
        self.assertEqual(result, '{"a": ["1", "two", "three"]}')
