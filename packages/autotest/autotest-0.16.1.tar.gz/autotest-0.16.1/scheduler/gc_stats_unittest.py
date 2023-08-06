#!/usr/bin/python

import logging
import unittest

try:
    import autotest.common as common
except ImportError:
    import common
from autotest.client.shared.test_utils import mock
from autotest.scheduler import gc_stats


class TestGcStats(unittest.TestCase):

    def setUp(self):
        self.god = mock.mock_god()

    def tearDown(self):
        self.god.unstub_all()

    def test_log_garbage_collector_stats(self):
        # Call this for code coverage.
        # Prevent log spam from this test but do test that the log
        # message formats correctly.
        def _mock_logging_func(message, *args):
            if args:
                message %= args
        self.god.stub_with(logging, 'debug', _mock_logging_func)
        self.god.stub_with(logging, 'info', _mock_logging_func)
        gc_stats._log_garbage_collector_stats()
        # Add a new dict, exercise the delta counting & printing code.
        y = {}
        gc_stats._log_garbage_collector_stats(1)


if __name__ == '__main__':
    unittest.main()
