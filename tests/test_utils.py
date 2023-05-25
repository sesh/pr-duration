import unittest

from pr_duration.cli import pretty_time_delta


class TimedeltaFormatTestCase(unittest.TestCase):
    def test_simple_timedelta(self):
        result = pretty_time_delta(12203)
        self.assertEqual(result, "3h23m23s")

    def test_short_timedelta(self):
        result = pretty_time_delta(12)
        self.assertEqual(result, "12s")

    def test_long_timedelta(self):
        result = pretty_time_delta(400 * 24 * 60 * 60)
        self.assertEqual(result, "400d0h0m0s")
