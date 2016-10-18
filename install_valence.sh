#!/bin/bash -       
#title           :install_valence.sh
#description     :This script will install valence package and deploys conf files
#author		 :Intel Corporation
#date            :17-10-2016
#version         :0.1    
#usage		 :bash install_valence.sh 
#==============================================================================

install_log=install_valence.log
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
echo "Current directory: $DIR" >> $install_log
if [ "$USER" != 'root' ]; then
	echo "You must be root to install."
	exit
fi
PYHOME=$(python -c "import site; print site.getsitepackages()[0]")
echo "Detected PYTHON HOME: $PYHOME" >> $install_log

# Copy the config files
cp $DIR/doc/source/init/valence-api.conf /tmp/valence-api.conf
sed -i s/\${CHUID}/$USER/  /tmp/valence-api.conf
#Use alternate sed delimiter because path will
#have /
sed -i "s#PYHOME#$PYHOME#" /tmp/valence-api.conf
mv /tmp/valence-api.conf /etc/init/valence-api.conf
echo "Setting up valence-api config" >> $install_log

cp $DIR/doc/source/init/valence-controller.conf /tmp/valence-controller.conf
sed -i s/\${CHUID}/$USER/   /tmp/valence-controller.conf
#Use alternate sed delimiter because path will
#have /
sed -i "s#PYHOME#$PYHOME#"   /tmp/valence-controller.conf
mv /tmp/valence-controller.conf /etc/init/valence-controller.conf
echo "Setting up valence-controller config" >> $install_log

# create conf directory for valence
mkdir /etc/valence
chown ${USER}:${USER} /etc/valence
cp etc/valence/valence.conf.sample /etc/valence/valence.conf

# create log directory for valence
mkdir /var/log/valence
chown ${USER}:${USER} /var/log/valence

echo "Invoking setup.py" >> $install_log
python setup.py install
if [ $? -ne 0 ]; then
	echo "ERROR: setup.py failed. Please fix the error and retry."
	exit
fi

echo "Installation Completed"
echo "To start api : sudo service valence-api start"
echo "To start controller : sudo service valence-controller start"
