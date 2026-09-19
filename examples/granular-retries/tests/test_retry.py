import unittest

from retry import cap, exponential


class RetryTests(unittest.TestCase):
    # [utest~retry-growth~1->req~retry-growth~1]
    def test_growth(self):
        for attempt in range(8):
            self.assertEqual(exponential(attempt), 2**attempt)

    # [utest~retry-cap~1->req~retry-cap~1]
    def test_cap(self):
        self.assertEqual(cap(0), 0)
        self.assertEqual(cap(7), 7)
        self.assertEqual(cap(8), 8)
        self.assertEqual(cap(100), 8)
