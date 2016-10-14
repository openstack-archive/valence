=========================
Openstack Valence Project
=========================

Valence is a service for lifecycle management of pooled bare-metal hardware infrastructure such as Intel(R) Rack Scale architecture which uses Redfish(TM) as one of the management protocols.
    
:Free software: Apache license
:Wiki: https://wiki.openstack.org/wiki/Valence
:Source: http://git.openstack.org/cgit/openstack/rsc
:Bugs: http://bugs.launchpad.net/openstack-valence

    
===========================
Download and Installation
===========================

The following steps capture how to install valence. All installation steps require super user permissions.

********************
Valence installation
********************

 1. Install software dependencies

    ``$ sudo apt-get install git python-pip rabbitmq-server libyaml-0-2 python-dev``

 2. Configure RabbitMq Server

     ``$ sudo rabbitmqctl add_user rsd rsd    #user this username/pwd in valence.conf``

     ``$ sudo rabbitmqctl set_user_tags rsd administrator``

     ``$ sudo rabbitmqctl set_permissions rsd ".*" ".*" ".*"``
   
 3. Clone the Valence code from git repo and change the directory to root Valence folder.

 4. Install all necessary software pre-requisites using the pip requirements file. 

    ``$ sudo -E pip install -r requirements.txt``

 5. Execute the 'install_valence.sh' file the Valence root directory. 

    ``$ ./install_valence.sh``
 
 6. Check the values in valence.conf located at /etc/valence/valence.conf   
         
     ``set the ip/credentials of podm for which this Valence will interact``

     ``set the rabbitmq user/password to the one given above(Step 2)``

 7. Check the values in /etc/init/valence-api.conf, /etc/init/valence-controller.conf 

 8. Start api and controller services
    
    ``$ sudo service valence-api start`` 

    ``$ sudo service valence-controller start``

 9. Logs are located at /var/logs/valence/

****************
GUI installation
****************
Please refer to the installation steps in the ui/README file. 


**********
Components
**********

Valence follows the typical OpenStack project setup. The components are listed below:

valence-api
-----------
A pecan based daemon to expose Valence REST APIs. The api service communicates to the controller through AMQP.

valence-controller
--------------
The controller implements all the handlers for Plasma-api. It reads requests from the AMQP queue, process it and send the reponse back to the caller.

valence-ui
--------
valence-ui provides a GUI interface to invoke Valence APIs. 

==========
Features
==========
Please refer the Valence blueprints for supported and in-the-pipeline features.
``https://blueprints.launchpad.net/plasma``


