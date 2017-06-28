#!/bin/bash
#title           :install_valence.sh
#description     :This script will install valence package and deploys conf files
#author          :Intel Corporation
#date            :17-10-2016
#version         :0.1
#usage           :sudo -E bash install_valence.sh
#notes           :Run this script as sudo user and not as root.
#                 This script is needed still valence is packaged in to .deb/.rpm
#==============================================================================

install_log=install_valence.log
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURR_USER="$(whoami)"

cd "$DIR"
echo "Current directory: $DIR" >> $install_log
if [ "$CURR_USER" != 'root' ]; then
    echo "You must be root to install."
    exit
fi

PYHOME="/usr/local/bin"
echo "Detected PYTHON HOME: $PYHOME" >> $install_log

# Copy the config files
echo "Setting up valence config" >> $install_log
sed "s/\${CHUID}/$CURR_USER/"  "$DIR"/etc/services-startup-conf/valence.conf > /tmp/valence.conf
# Use alternate sed delimiter because path will have /
sed -i "s#PYHOME#$PYHOME#" /tmp/valence.conf
mv /tmp/valence.conf /etc/init/valence.conf
# Valence service file required at this path for starting service using systemctl
if [ -d "/etc/systemd/system" ]; then
    cp "$DIR"/etc/services-startup-conf/valence.service /etc/systemd/system/valence.service
fi

# Generate initial sample config file.
echo "Generating sample config file" >> $install_log
pip install tox
tox -egenconfig

# create conf directory for valence if it doesn't exist
if [ ! -d "/etc/valence" ]; then
    mkdir /etc/valence
fi
chown "$CURR_USER":"$CURR_USER" /etc/valence
VALENCE_CONF=/etc/valence/valence.conf
mv "$DIR"/etc/valence.conf.sample "$VALENCE_CONF"

sudo sed -i "s/#debug\s*=.*/debug=true/" $VALENCE_CONF
sudo sed -i "s/#log_level\s*=.*/log_level=debug/" $VALENCE_CONF
sudo sed -i "s/#log_file\s*=.*/log_file=/var/log/valence/valence.log/" $VALENCE_CONF
sudo sed -i "s/#bind_host\s*=.*/bind_host=0.0.0.0/" $VALENCE_CONF
sudo sed -i "s/#bind_port\s*=.*/bind_port=8181/" $VALENCE_CONF
sudo sed -i "s/#timeout\s*=.*/timeout=1000/" $VALENCE_CONF
sudo sed -i "s/#workers\s*=.*/workers=4/" $VALENCE_CONF
sudo sed -i "s/#host\s*=.*/host=localhost/" $VALENCE_CONF
sudo sed -i "s/#port\s*=.*/port=2379/" $VALENCE_CONF

# create log directory for valence if it doesn't exist
if [ ! -d "/var/log/valence" ]; then
    mkdir /var/log/valence
fi
chown "$CURR_USER":"$CURR_USER" /var/log/valence

echo "Installing dependencies from requirements.txt" >> $install_log
pip install -r requirements.txt

echo "Installing the etcd database" >> $install_log
ETCD_VER=v3.1.2
DOWNLOAD_URL=https://github.com/coreos/etcd/releases/download
curl -L ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz -o /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz
mkdir -p /var/etcd && tar xzvf /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /var/etcd --strip-components=1
chown "$CURR_USER":"$CURR_USER" /var/etcd
mv /var/etcd/etcd /usr/local/bin/etcd && mv /var/etcd/etcdctl /usr/local/bin/etcdctl
# Etcd service file required at this path for starting service using systemctl
if [ -d "/etc/systemd/system" ]; then
    cp "$DIR"/etc/services-startup-conf/etcd.service /etc/systemd/system/etcd.service
fi

sed "s/\${CHUID}/$CURR_USER/"  "$DIR"/etc/services-startup-conf/etcd.conf > /etc/init/etcd.conf

echo "Starting etcd database" >> $install_log
service etcd start
ETCD_STATUS=$?
sleep 2
timeout=30
attempt=1
until [[ $ETCD_STATUS = 0 ]]
do
  service etcd status
  ETCD_STATUS=$?
  sleep 1
  attempt=$((attempt+1))
  if [[ $attempt -eq timeout ]]
  then
    echo "Database failed to start, aborting installation."
    rm -rf /var/etcd /usr/local/bin/etcd /usr/local/bin/etcdctl
    exit
  fi
done

echo "Adding database directories" >> $install_log
etcdctl --endpoints=127.0.0.1:2379 mkdir /nodes
etcdctl --endpoints=127.0.0.1:2379 mkdir /flavors
etcdctl --endpoints=127.0.0.1:2379 mkdir /pod_managers

echo "Invoking setup.py" >> $install_log
python setup.py install
if [ $? -ne 0 ]; then
    echo "ERROR: setup.py failed. Please check $install_log for details.
          Please fix the error and retry."
    exit
fi

echo "Installation Completed"
echo "To start valence : sudo service valence start"
