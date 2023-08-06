#!/usr/bin/python

import unittest
try:
    import autotest.common as common
except ImportError:
    import common

from autotest.server.hosts import remote


class test_remote_host(unittest.TestCase):

    def test_has_hostname(self):
        host = remote.RemoteHost("myhost")
        self.assertEqual(host.hostname, "myhost")


if __name__ == "__main__":
    unittest.main()
