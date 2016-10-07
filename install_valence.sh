#!/bin/bash -       
#title           :install_valence.sh
#description     :This script will install valence package and deploys conf files
#author		 :Intel Corporation
#date            :21-09-2016
#version         :0.1    
#usage		 :bash mkscript.sh
#notes           :Run this script as sudo user and not as root.
#                 This script is needed still valence is packaged in to .deb/.rpm 
#==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $USER

cd $DIR

echo "Executing the script inside "
pwd



# Copy the config files
sed s/\${CHUID}/$USER/  $DIR/doc/source/init/valence-api.conf > /tmp/valence-api.conf
sudo mv /tmp/valence-api.conf /etc/init/valence-api.conf
sed s/\${CHUID}/$USER/  $DIR/doc/source/init/valence-controller.conf > /tmp/valence-controller.conf
sudo mv /tmp/valence-controller.conf /etc/init/valence-controller.conf

# create conf directory for valence
sudo mkdir /etc/valence
sudo chown ${USER}:${USER} /etc/valence
sudo cp etc/valence/valence.conf.sample /etc/valence/valence.conf


# create log directory for valence
sudo mkdir /var/log/valence
sudo chown ${USER}:${USER} /var/log/valence

python setup.py install --user

echo "Installation Completed"
echo "To start api : service valence-api start"
echo "To start controller : service valence-controller start"
