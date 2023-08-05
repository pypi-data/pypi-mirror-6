#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = '01388863189'
#
# Done by Gabriel Abdalla Cavalcante Silva at Receita Federal do Brasil,
#
# Licensed under the Apache License, Version 2.0, that can be viewed at:
#   http://www.apache.org/licenses/LICENSE-2.0
#
"""
Tests the manage module and the vmware_tests.py module.
"""
import unittest
import ConfigParser
from vunit_cfg import create_vmtest_cfg, read_vmtest_cfg


class ManagementFunctionsTest(unittest.TestCase):
    """ Contains all manage tests."""
    def setUp(self):
        self.vcenter_user = 'vcenter'
        self.vcenter_pass = 'vcenter123'
        self.vcenter_server = 'vcenter.domain.com'
        self.vcenter_dcenter = 'myDCenter'
        self.vcenter_cluster = 'myCluster'

        self.esxi_user = 'esxi'
        self.esxi_pass = 'esxi123'
        self.esxi_hosts = str(['host1', 'host2'])

        self.cfg = 'vmware_test.cfg'

    def assert_default_attrs(self, cfg):
        """ Do the general tests of a configuration object attributes."""
        self.assertTrue(cfg.has_section('Vcenter'))
        self.assertTrue(cfg.has_section('Host'))

        self.assertEqual(self.vcenter_user, cfg.get('Vcenter', 'user'))
        self.assertEqual(self.vcenter_pass, cfg.get('Vcenter', 'pass'))
        self.assertEqual(self.vcenter_server, cfg.get('Vcenter', 'server'))

        self.assertEqual(self.esxi_user, cfg.get('Host', 'user'))
        self.assertEqual(self.esxi_pass, cfg.get('Host', 'pass'))
        self.assertEqual(self.esxi_hosts, cfg.get('Host', 'cluster'))

    def test_create_vmtest_cfg(self):
        """ Test if the create_vmtest_cfg works as expected. """
        cfg = create_vmtest_cfg(vuser=self.vcenter_user,
                                vpass=self.vcenter_pass,
                                vserver=self.vcenter_server,
                                vdcenter=self.vcenter_dcenter,
                                vdcluster=self.vcenter_cluster,
                                huser=self.esxi_user,
                                hpass=self.esxi_pass,
                                hcluster=self.esxi_hosts,
                                cfg=self.cfg,
                                debug=True)

        self.assertIsInstance(cfg, ConfigParser.RawConfigParser)
        self.assert_default_attrs(cfg)

    def test_read_vmtest_cfg(self):
        """ Test if the read_vm_test_cfg works as expected"""
        cfg = read_vmtest_cfg(cfg=self.cfg, debug=True)
        self.assertIsInstance(cfg, ConfigParser.ConfigParser)
        self.assert_default_attrs(cfg)


if __name__ == '__main__':
    unittest.main()

