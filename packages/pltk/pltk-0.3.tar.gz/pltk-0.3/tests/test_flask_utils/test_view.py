"""Test view helpers."""
import unittest
import datetime

from pltk.flask_utils.view import _json_handler, View


class TestJsonHandler(unittest.TestCase):
    """Test json handler."""
    def test_datetime_formatting(self):
        """Test datetime formatting."""
        obj = datetime.datetime(
            year=2012,
            month=9,
            day=11,
            hour=10,
            minute=30,
            second=10,
            microsecond=10
        )
        self.assertEqual(_json_handler(obj), '2012-09-11 10:30:10')

    def test_unserializable(self):
        """An int can't be serialized."""
        try:
            _json_handler(1)
            success = False
        except TypeError:
            # An int can not be serialized, so, this error is the
            # success.
            success = True
        self.assertTrue(success)


class TestView(unittest.TestCase):
    """Test view."""
    view = View()

    def test_dict_keys_to_string(self):
        """Test the method that allow compatibility with python 2.6 changing
        the keys of the dict from unicode to string.
        """
        kwargs = self.view.dict_keys_to_string({u'test': 'test'})
        # without the unicode key
        self.assertEqual(kwargs, {'test': 'test'})

    def test_invalid_value(self):
        """Test behavior when invalid values are passed."""
        # force an error and check that I receive the same that I send
        self.assertEqual(self.view.dict_keys_to_string(1), 1)
