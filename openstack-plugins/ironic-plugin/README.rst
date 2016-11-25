
===============================
OpenStack Ironic Valence Plugin
===============================

Spec link : https://review.openstack.org/#/c/402288/

BP link : https://blueprints.launchpad.net/openstack-valence/+spec/openstack-components-plugin

This doc will tell you how to setup a driver for valence in ironic.
OpenStack version : Newton.

Step one: Creat a new driver in ironic
======================================

In the ironic.conf file , there is an opetion shows which drivers are enabled in ironic.
Add our new driver named valence here, like this:
```
enabled_drivers = pxe_ipmitool, valence
```

Step two: Enable valence dirver
===============================
After insert a driver in `ironic.conf`, we need to enbale the driver with driver instance file.
First copy the valence driver instance file to ironic source dir:
```
cp openstack-plugins/ironic-plugin/drivers/valence.py <OpenStack-IronicHomeDir>/driver/
mkdir -p <OpenStack-IronicHomeDir>/driver/modules/valence
cp openstack-plugins/ironic-plugin/drivers/modules/valece/* <OpenStack-IronicHomeDir>/driver/modules/valence/
```
Then add items in `<OpenStack-HomeDir>/ironic-xxxxxxx.egg-info/entry_points.txt` under `[ironic.drivers]`
option, like this:
```
valence = ironic.drivers.valence:ValenceDriver
```
Now, restart ironic service and we could check the driver list to show the result.
```
source /root/keystonerc_admin
service openstack-ironic-api restart
service openstacl-ironic-conductor restart
ironic driver-list
```

Step three: fill features into the driver
=========================================
As you see , you can find out there are three propeties defined in the driver instance file:`valence.py`
```
self.power = power.ValencePower()
self.management = management.ValenceManagement()
self.vendor = vendor.ValenceVendor()
```
These three properties are base on the `base.BaseDriver` properties. To fill featurs into the driver
means to add properties for the driver. And we just need to figure out the map releation between
features and properties.Actually , we would take all valence API caller into those properties.

There in an example in the `vendor` perporty. We can test this by ironic commands
```
source /root/keystonerc_admin
ironic --debug driver-vendor-passthru valence test_connection
```
The result would show the function returns defined in `vendor.py`.If we define some valence API caller
here we could connect with valence really.

So we can make connection between ironic and valence by our customized commands or featurs.

