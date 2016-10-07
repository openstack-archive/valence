=======================
Openstack RSC Project
=======================

Rack Scale Controller (RSC) is a service for lifecycle management of pooled bare-metal hardware infrastructure such as Intel(R) Rack Scale architecture which uses Redfish(TM) as one of the management protocols.
    
:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Rsc
:Source: http://git.openstack.org/cgit/openstack/rsc
:Bugs: http://bugs.launchpad.net/plasma

    
===========================
Download and Installation
===========================

The following steps capture how to install rsc. All installation steps require super user permissions.

********************
RSC installation
********************

 1. Install software dependencies

    ``$ sudo apt-get install git python-pip rabbitmq-server libyaml-0-2 python-dev``

 2. Configure RabbitMq Server

     ``$ sudo rabbitmqctl add_user rsd rsd    #user this username/pwd in rsc.conf``

     ``$ sudo rabbitmqctl set_user_tags rsd administrator``

     ``$ sudo rabbitmqctl set_permissions rsd ".*" ".*" ".*"``
   
 3. Clone the RSC code from git repo and change the directory to root RSC folder.

 4. Install all necessary software pre-requisites using the pip requirements file. 

    ``$ sudo -E pip install -r requirements.txt``

 5. Execute the 'install_rsc.sh' file the RSC root directory. 

    ``$ ./install_rsc.sh``
 
 6. Check the values in rsc.conf located at /etc/rsc/rsc.conf   
         
     ``set the ip/credentials of podm for which this RSC will interact``

     ``set the rabbitmq user/password to the one given above(Step 2)``

 7. Check the values in /etc/init/rsc-api.conf, /etc/init/rsc-controller.conf 

 8. Start api and controller services
    
    ``$ service rsc-api start`` 

    ``$ service rsc-controller start``

 9. Logs are located at /var/logs/rsc/

****************
GUI installation
****************
Please refer to the installation steps in the ui/README file. 


**********
Components
**********

RSC follows the typical OpenStack project setup. The components are listed below:

rsc-api
-----------
A pecan based daemon to expose RSC REST APIs. The api service communicates to the controller through AMQP.

rsc-controller
--------------
The controller implements all the handlers for Plasma-api. It reads requests from the AMQP queue, process it and send the reponse back to the caller.

rsc-ui
--------
rsc-ui provides a GUI interface to invoke RSC APIs. 

==========
Features
==========
Please refer the RSC blueprints for supported and in-the-pipeline features.
``https://blueprints.launchpad.net/plasma``


