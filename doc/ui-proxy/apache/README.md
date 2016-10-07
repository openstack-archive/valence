Apache proxy service to pod-manager API
=======================================

This manual has been verified on Ubuntu 16.04 + Apache (2.4.18-2ubuntu3.1).

##Install
1. Use package manager tool on your distribution to install apache server.
   ```
   sudo apt-get install apache2
   ```
2. Enable all related modules for Apache server.
   ```
   sudo a2enmod proxy_http proxy ssl headers
   ```
3. Setup virtual host for proxy to podm.
   ```
   sudo cp podm-proxy.conf /etc/apache2/sites-available
   sudo a2ensite podm-proxy
   ```
4. Add listening port 6000.
   Add "Listen 6000" into Apaches port setting file /etc/apache2/ports.conf.
   * If need, you can change it to any available port in your server. In this case, please remember to update
     "<VirtualHost *:6000>" in /etc/apache2/sites-available/podm-proxy.conf.
5. Update podm address in /etc/apache2/sites-available/podm-proxy.conf.
   By default, the podm api is pointed to https://127.0.0.1:8443/. Update it to fit your environment.
6. Restart Apache server.
   ```
   sudo systemctl restart apache2
   ```

The proxy is available under http://127.0.0.1:6000/redfish/v1.
   ```
   curl http://127.0.0.1:6000/redfish/v1/
   {
     "@odata.context" : "/redfish/v1/$metadata#ServiceRoot",
     "@odata.id" : "/redfish/v1",
     "@odata.type" : "#ServiceRoot.1.0.0.ServiceRoot",
     "Id" : "ServiceRoot",
     "Name" : "Service root",
     "RedfishVersion" : "1.0.0",
     "UUID" : "3c414ee3-bd28-4e6c-b9e8-fd8008dbd0ce",
     "Chassis" : {
       "@odata.id" : "/redfish/v1/Chassis"
     },
     "Services" : {
       "@odata.id" : "/redfish/v1/Services"
     },
     "Systems" : {
       "@odata.id" : "/redfish/v1/Systems"
     },
     "Managers" : {
       "@odata.id" : "/redfish/v1/Managers"
     },
     "EventService" : {
       "@odata.id" : "/redfish/v1/EventService"
     },
     "Nodes" : {
       "@odata.id" : "/redfish/v1/Nodes"
     },
     "EthernetSwitches" : {
       "@odata.id" : "/redfish/v1/EthernetSwitches"
     },
     "Oem" : {
       "Intel_RackScale" : {
         "@odata.type" : "#Intel.Oem.ServiceRoot",
         "ApiVersion" : "1.2.0"
       }
     },
     "Links" : { }
   }
   ```
