=========================
Openstack Valence Project
=========================

********
Overview
********

Valence is a service for lifecycle management of pooled bare-metal hardware
infrastructure.  The concept of pooled storage (SSDs or nvmE) disaggregated
from compute nodes and network disaggregated from compute and storage
provides the flexibility to compose and uses as and when the cloud requires
more server resources. Valence provides the capability "compose" hardware nodes
and release resources as needed by the overcloud.

Valence supports Redfish as default management protocol to communicate
to hardware. It supports Rack Scale Design (RSD), Open architecture for management
of disaggregated server hardware resources, which is standardized in Redfish.
Valence also provides capability to manage other vendors disaggregated hardware
using their respective drivers other than Redfish.

:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Valence
:Source: http://git.openstack.org/cgit/openstack/valence
:Bugs: https://bugs.launchpad.net/openstack-valence
