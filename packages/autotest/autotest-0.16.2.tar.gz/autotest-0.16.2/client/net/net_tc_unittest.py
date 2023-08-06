#!/usr/bin/python

# TODO(chavey) complete all the unit test in this file

import unittest
import os
try:
    import autotest.common as common
except ImportError:
    import common
from autotest.client import utils
from autotest.client.shared.test_utils import mock


class TestNetUtils(unittest.TestCase):

    def setUp(self):
        self.god = mock.mock_god()
        self.god.stub_function(utils, "system")
        self.god.stub_function(utils, "system_output")
        os.environ['AUTODIR'] = "autodir"

    def tearDown(self):
        self.god.unstub_all()
        del os.environ['AUTODIR']

    #
    # test tcclass
    #
    def test_tcclass_get_leaf_qdisc(self):
        pass

    def test_tcclass_get_parent_class(self):
        pass

    def test_tcclass_set_parent_class(self):
        pass

    def test_tcclass_get_minor(self):
        pass

    def test_tcclass_id(self):
        pass

    def test_tcclass_add_child(self):
        pass

    def test_tcclass_setup(self):
        pass

    def test_tcclass_restore(self):
        pass

    #
    # test tcfilter
    #
    def test_tcfilter_get_parent_qdisc(self):
        pass

    def test_tcfilter_set_parent_qdisc(self):
        pass

    def test_tcfilter_get_dest_qdisc(self):
        pass

    def test_tcfilter_set_dest_qdisc(self):
        pass

    def test_tcfilter_get_protocol(self):
        pass

    def test_tcfilter_set_protocol(self):
        pass

    def test_tcfilter_get_priority(self):
        pass

    def test_tcfilter_set_priority(self):
        pass

    def test_tcfilter_get_handle(self):
        pass

    def test_tcfilter_set_handle(self):
        pass

    def test_tcfilter_tc_cmd(self):
        pass

    def test_tcfilter_setup(self):
        pass

    def test_tcfilter_restore(self):
        pass

    #
    # test u32filter
    #
    def test_u32filter_add_rule(self):
        pass

    def test_u32filter_setup(self):
        pass

    def test_u32filter_restore(self):
        pass

    #
    # test qdisc
    #
    def test_qdisc_add_class(self):
        pass

    def test_qdisc_add_filter(self):
        pass

    def test_qdisc_setup(self):
        pass

    def test_qdisc_restore(self):
        pass

    #
    # test prio
    #
    def test_prio_setup(self):
        pass

    def test_prio_get_class(self):
        pass

    #
    # test pfifo
    #
    def test_pfifo_setup(self):
        pass

    #
    # test netem
    #
    def test_netem_add_param(self):
        pass

    def test_netem_setup(self):
        pass


if __name__ == "__main__":
    unittest.main()
