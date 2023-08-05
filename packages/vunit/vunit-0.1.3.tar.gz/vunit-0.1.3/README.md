Vmware-unittests
----------------

Unit tests for Vcenter and ESXI which provides some usefull verifications for
resources before or after maintenances.

Introduction
------------

Vunit is a python script that relies on pysphere library to test
the Vmware Esxi and Vcenter environment with some usefull tests. With this tool,
system admins can verify impacts on environments before or after a maintenance.

Installation
------------

1. Install vunit:

You can install the Vmware-unittests through pip:

`pip install vunit`

The sdist package can be downloaded as well in the pypi page:

https://pypi.python.org/pypi/vunit

Requirements
------------

Before the use, the following requirements must be met:

 * A read-only credential to the Vmware Vcenter must be available;
 * A local read-only credential to all Esxi Hosts must be available.
 
Configuration
-------------
Before the first use, the configuration file need to be created with the 
following command:

`vunit_cfg -vuser <VCENTER USER> -vpass <VCENTER PASS> -vserver <VCENTER SERVER>
-huser <HOST USER> -hpass <HOST PASS> -hlist <HOST LIST>`

Below, a example of use:

`vunit_cfg -vuser myuser -vpass mypass -vserver vcenter.mydomain.com
-huser myhostuser -hpass myhostpass -hlist 192.168.1.1,192.168.1.2,192.168.1.3`

With this, a vmware.cfg file will be created at the current directory.

As we can see, some parameters are necessary to initial configuration, as 
described:

 * vuser: A user that have read-only access to the Vcenter Console.
 * vpass: The password of the vuser.
 * vserver: IP Address or Name(FQDN) of the Vmware Vcenter Server.
 
 * huser: A user that have local read-only to all hosts.
 * hpass: The password of the huser.
 * hlist: The list of IP Addresses and/or Names of hosts, separated by commas &
 without spaces (eg: 192.168.100.100,192.168.100.101).

How to Use
----------

There are three types of tests available:

* VmwareBasicTests: tests basic operations, like logons and creates resources 
lists that are used later by the VmwareTurnOn.

VmwareBasicTests is designed for test small impacts (eg: SGBD
restore/backups, Vcenter Server Restarts and general configuration changes) and
create resources lists, which are files that contains pickled information about
all resources of enviroments that are used by the 'VmwareTurnOn' tests.

For maintentances purposes, always run this test BEFORE any changes in the
enviroment.

* VmwareTurnOff: verify if the environment is fully disconnected/turned off.

VmwareTurnOff is designed for test if the environment is really disconnected
(eg: no vms on, no hosts out of maintenance, etc).

* VmwareTurnOn: test if the enviroment is functional.

VmwareTurnOn is designed to test impacts AFTER a full maintenance of the environment.
It relies on the resources files, previously created with the VmwareBasicTests
and test if all online resources are the same of the before of the maintenance.

The tests can be started through the 'vmwatest' script, which have the following syntax:

`vmwtest.py --test {basic, turnoff, turnon}`

The options of the '--test' parameter are the tests with a simple syntax use, like:

`vmtest.py --test basic`
`vmtest.py --test turnoff`
`vmtest.py --test turnon`

License
-------

Licensed under the Apache License, Version 2.0, that can be viewed at:
  http://www.apache.org/licenses/LICENSE-2.0

Credits
-------
* [Gabriel Abdalla Cavalcante](https://github.com/gcavalcante8808)
