#!/bin/bash -       
#title           :install_rsc.sh
#description     :This script will install rsc package and deploys conf files
#author		 :Intel Corporation
#date            :21-09-2016
#version         :0.1    
#usage		 :bash mkscript.sh
#notes           :Run this script as sudo user and not as root.
#                 This script is needed still rsc is packaged in to .deb/.rpm 
#==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $USER

cd $DIR

echo "Executing the script inside "
pwd



# Copy the config files
sed s/\${CHUID}/$USER/  $DIR/doc/source/init/rsc-api.conf > /tmp/rsc-api.conf
sudo mv /tmp/rsc-api.conf /etc/init/rsc-api.conf
sed s/\${CHUID}/$USER/  $DIR/doc/source/init/rsc-controller.conf > /tmp/rsc-controller.conf
sudo mv /tmp/rsc-controller.conf /etc/init/rsc-controller.conf

# create conf directory for rsc
sudo mkdir /etc/rsc
sudo chown ${USER}:${USER} /etc/rsc
sudo cp etc/rsc/rsc.conf.sample /etc/rsc/rsc.conf


# create log directory for rsc
sudo mkdir /var/log/rsc
sudo chown ${USER}:${USER} /var/log/rsc

python setup.py install --user

echo "Installation Completed"
echo "To start api : service rsc-api start"
echo "To start controller : service rsc-controller start"
