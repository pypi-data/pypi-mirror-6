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
This module contains all instructions to test the VMware Infraestructure.
"""
import pickle
import socket
import argparse
import unittest
from pysphere import VIServer, VIApiException, VIMor, VIProperty
from vunit_cfg import read_vmtest_cfg
from vunit.vunit_utils import write_resource_file

CREDS = read_vmtest_cfg(cfg="vmware.cfg")


def vcenter_connect():
    """ Connect to the vcenter. """
    server = VIServer()
    server.connect(CREDS.get('Vcenter', 'server'),
                   CREDS.get('Vcenter', 'user'),
                   CREDS.get('Vcenter', 'pass'))

    return server


def host_connect(host):
    """ Connect to a host. """
    server = VIServer()
    server.connect(host, CREDS.get('Host', 'user'),
                   CREDS.get('Host', 'pass'))

    return server


class VmwareBasicTests(unittest.TestCase):
    """ Just do all basic tests."""

    def test_user_can_login_on_vcenter(self):
        """Is the Vcenter capable at this moment to login an Active Directory
        User?
        """
        try:
            server = vcenter_connect()
            server.disconnect()
        except VIApiException:
            self.fail("Servidor Indisponivel ou Usuario sem Acesso")

    def test_user_can_login_on_host(self):
        """Local Users can login into hosts separately?"""
        for host in CREDS.get('Host', 'Cluster').split(","):
            try:
                server = host_connect(host)
                server.disconnect()
            except VIApiException:
                self.fail("Service Unavailable or Unknown User/Password")

    def test_vmwareapi_vcenter_type(self):
        """ Is The API Type of 10.61.12.116 a vcenter type?"""
        server = vcenter_connect()
        server_type = server.get_api_type()
        self.assertEqual('VirtualCenter', server_type)
        server.disconnect()

    def test_vmwareapi_host_type(self):
        """ Is the Api of the hosts a Host API Type?"""
        for host in CREDS.get('Host', 'Cluster').split(","):
            server = host_connect(host)
            server_type = server.get_api_type()
            self.assertEqual('HostAgent', server_type)
            server.disconnect()

    def test_vmware_version_vcenter(self):
        """ Is the Vmware version at 5.1?"""
        server = VIServer()
        server.connect(CREDS.get('Vcenter', 'server'),
                       CREDS.get('Vcenter', 'user'),
                       CREDS.get('Vcenter', 'pass'))
        api = server.get_api_version()
        self.assertEqual('5.1', api)
        server.disconnect()

    def test_vmware_version_host(self):
        """ Is the Vmware version at 5.1?"""
        for host in CREDS.get('Host', 'Cluster').split(","):
            server = host_connect(host)
            api = server.get_api_version()
            self.assertEqual('5.1', api)
            server.disconnect()

    def test_and_write_poweredon_vms(self):
        """ Get and write all poweredon vms into a file, that will be used
        later at the VMPowerOn Test."""
        server = vcenter_connect()
        vms = server.get_registered_vms(status='poweredOn')
        write_resource_file('vm_number.txt', vms)
        server.disconnect()

    def test_and_write_datastores(self):
        """Get and write all available datastores into a file."""
        server = vcenter_connect()
        write_resource_file('datastores.txt',
                            server.get_datastores().values())
        server.disconnect()

    def test_and_write_datacenters(self):
        """ Get and write all available datacenters into a file."""
        server = vcenter_connect()
        write_resource_file('datacenters.txt',
                            server.get_datacenters().values())
        server.disconnect()

    def test_and_write_clusters(self):
        """ Get and write all available clusters into a file. """
        server = vcenter_connect()
        write_resource_file('clusters.txt', server.get_datacenters().values())
        server.disconnect()

#######
####### DIA DE DESLIGAMENTO DO VMWARE
#######


class VmwareTurnOff(unittest.TestCase):
    """ Verifica se todas as ações para o desligamento do ambiente foram
        tomadas corretamente."""

    def test_if_vcenter_is_available(self):
        """O Vcenter ainda está ligado?"""
        try:
            server = vcenter_connect()
            server.disconnect()
            self.fail(u"O Vcenter ainda está disponível")
        except socket.error:
            pass

    def test_if_drs_is_deactivated(self):
        """Todos os hosts estão com o DRS desativado?"""
        self.fail('NotImplemented')

    def test_if_all_vms_are_off(self):
        """Todas as máquinas virtuais estão desligadas?"""
        for host in CREDS.get('Host', 'Cluster').split(","):
            server = host_connect(host)
            off = server.get_registered_vms(status='poweredOn')
            self.assertEqual(0, len(off), u"")

    def test_if_all_hosts_are_in_maintenance(self):
        """Todos os hosts estão em modo de manutenção?"""
        server = vcenter_connect()
        hosts = server.get_hosts()

        for host in hosts:
            host_mor = VIMor(host, 'HostSystem')
            host_props = VIProperty(server, host_mor)
            self.assertTrue(host_props.runtime.inMaintenanceMode,
                            u"Nem todos os hosts estão desativados")

#######
####### DIA DE ATIVAÇÃO DO VMWARE
#######


class VmwareTurnOn(unittest.TestCase):
    """ Testes a serem realizados após o vmware voltar a ser ligado.
        Estes testes verificam se o ambiente está funcionando da mesma
        forma de antes de ser desligado.
    """

    def setUp(self):
        """Connect To Vmware."""
        self.server = vcenter_connect()

    def tearDown(self):
        """Disconnects from Vmware."""
        self.server.disconnect()

    def test_if_all_hosts_arent_in_maintenance(self):
        """Are all the hosts out of the maintenance?"""
        hosts = self.server.get_hosts()
        for host in hosts:
            host_mor = VIMor(host, 'HostSystem')
            host_props = VIProperty(self.server, host_mor)
            self.assertFalse(host_props.runtime.inMaintenanceMode,
                             u"Host Not Activated:{}".format(
                                 host))

    def test_if_all_previous_datacenters_are_available(self):
        """Are all previous Datacenters available?"""
        prev_dcs = pickle.load(open('resource_lists/datacenters.txt'))
        online_dcs = self.server.get_datacenters().values()
        diff_dcs = set(prev_dcs).difference(online_dcs)
        self.assertEqual(set(), diff_dcs, diff_dcs)

    def test_if_all_previous_clusters_are_available(self):
        """Are all previous clusters available?"""
        prev_cls = pickle.load(open('resource_lists/clusters.txt'))
        online_cls = self.server.get_datacenters().values()
        diff_cls = set(prev_cls).difference(online_cls)
        self.assertEqual(set(), diff_cls, diff_cls)

    def test_if_all_previous_started_machines_are_available(self):
        """Are all previous poweredOn vms the same?"""
        prev_vms = pickle.load(open('resource_lists/vm_number.txt', 'rb'))
        online_vms = self.server.get_registered_vms(status='poweredOn')
        diff_vms = set(prev_vms).difference(online_vms)
        self.assertEqual(set(), diff_vms, diff_vms)

    def test_if_all_previous_ds_are_available(self):
        """Are all previous available datastores the same?"""
        prev_ds = pickle.load(open('resource_lists/datastores.txt', 'rb'))
        online_ds = self.server.get_datastores().values()
        diff_ds = set(prev_ds).difference(online_ds)
        self.assertEqual(set(), diff_ds, diff_ds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', choices=['basic', 'turnoff', 'turnon'],
                        required=True)
    args = parser.parse_args()

    if args.test == 'basic':
        suite = unittest.TestLoader().loadTestsFromTestCase(VmwareBasicTests)
        unittest.TextTestRunner().run(suite)
    elif args.test == 'turnoff':
        suite = unittest.TestLoader().loadTestsFromTestCase(VmwareTurnOff)
        unittest.TextTestRunner().run(suite)
    elif args.test == 'turnon':
        suite = unittest.TestLoader().loadTestsFromTestCase(VmwareTurnOn)
        unittest.TextTestRunner().run(suite)
