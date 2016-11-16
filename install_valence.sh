#!/bin/bash
#title           :install_valence.sh
#description     :This script will install valence package and deploys conf files
#author		 :Intel Corporation
#date            :17-10-2016
#version         :0.1
#usage		 :sudo -E bash install_valence.sh
#notes           :Run this script as sudo user and not as root.
#                 This script is needed still valence is packaged in to .deb/.rpm
#==============================================================================

install_log=install_valence.log
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR
echo "Current directory: $DIR" >> $install_log
if [ `whoami` != 'root' ]; then
	echo "You must be root to install."
	exit
fi

PYHOME="/usr/local/bin"
echo "Detected PYTHON HOME: $PYHOME" >> $install_log

# Copy the config files
echo "Setting up valence config" >> $install_log
sed s/\${CHUID}/$USER/  $DIR/doc/source/init/valence.conf > /tmp/valence.conf
#Use alternate sed delimiter because path will have /
sed -i "s#PYHOME#$PYHOME#" /tmp/valence.conf
mv /tmp/valence.conf /etc/init/valence.conf

# create conf directory for valence if it doesn't exist
if [ ! -d "/etc/valence" ]; then
    mkdir /etc/valence
fi
chown ${USER}:${USER} /etc/valence
cp etc/valence/valence.conf.sample /etc/valence/valence.conf

# create log directory for valence if it doesn't exist
if [ ! -d "/var/log/valence" ]; then
    mkdir /var/log/valence
fi
chown ${USER}:${USER} /var/log/valence

echo "Installing dependencies from requirements.txt" >> $install_log
pip install -r requirements.txt

echo "Invoking setup.py" >> $install_log
python setup.py install
if [ $? -ne 0 ]; then
	echo "ERROR: setup.py failed. Please check $install_log for details.
          Please fix the error and retry."
	exit
fi

echo "Installation Completed"
echo "To start valence : sudo service valence start"
