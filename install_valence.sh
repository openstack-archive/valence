#!/bin/bash
#title           :install_valence.sh
#description     :This script will install valence package and deploys conf files on
#                 centos or ubuntu
#author          :Intel,99Cloud
#date            :14-10-2017
#version         :0.2
#usage           :sudo -E bash install_valence.sh
#notes           :Run this script as sudo user and not as root.
#                 This script is needed still valence is packaged in to .deb/.rpm
#==============================================================================

INSTALL_LOG="/var/log/valence/valence_install.log"
OPERATION_SYSTEM="centos"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURR_USER="$(whoami)"

function check_os()
{
    if [ `cat /proc/version |grep -i ubuntu |wc -l` -gt 0 ];then
        OPERATION_SYSTEM='ubuntu'
    elif [ `cat /proc/version |grep -i centos |wc -l` -gt 0 ];then
        OPERATION_SYSTEM="centos"
    fi
    if [ "$CURR_USER" != 'root' ]; then
        echo "You must be root to install."
        exit
    fi
}

function install_dependency_package()
{
    check_os
    echo current os is $OPERATION_SYSTEM
    if [ $OPERATION_SYSTEM = "ubuntu" ];then
        echo '--------------'
        apt update -y
        apt install -y python-pip wget git
    elif [ $OPERATION_SYSTEM = "centos" ];then
        yum install -y epel-release
        yum install -y python-pip wget git
    fi
}

# create_or_delete_etcd mkdir: create database
# create_or_delete_etcd "rm -rf": delelte database
function create_or_delete_etcd()
{
    etcdctl --endpoints=127.0.0.1:2379 $1 /nodes
    etcdctl --endpoints=127.0.0.1:2379 $1 /flavors
    etcdctl --endpoints=127.0.0.1:2379 $1 /pod_managers
}

function start_etcd()
{
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
        if [[ $attempt -eq timeout ]];then
            echo "Database failed to start, aborting installation."
            create_or_delete_etcd "rm -rf"
            rm -rf /var/etcd /usr/local/bin/etcd /usr/local/bin/etcdctl
            exit
        fi
    done
}

function install_etcd()
{
    echo "0:------+++++++++++"
    ETCD_VER=v3.1.2
    DOWNLOAD_URL=https://github.com/coreos/etcd/releases/download
    echo "1:------+++++++++++"
    echo "etcd-${ETCD_VER}-linux-amd64.tar.gz"
    echo `ls -h /tmp`
    if [ ! -f /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz ];then
        echo "Downloading etcd into /tmp from ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz" >> $INSTALL_LOG
        curl -L ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz -o /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz
        if [ $? -ne 0 ];then
            echo "Downloading etcd into /tmp from ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz failed!!!"
            rm -f /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz
            echo "Downloading etcd into /tmp from ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz failed!!!" >> $INSTALL_LOG
            exit
        fi
    else
        echo "2:------+++++++++++"
        echo "etcd-${ETCD_VER}-linux-amd64.tar.gz already exist in /tmp"
    fi
    echo "3:------+++++++++++"
    mkdir -p /var/etcd && tar xzvf /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /var/etcd --strip-components=1
    chown "$CURR_USER":"$CURR_USER" /var/etcd
    mv /var/etcd/etcd /usr/local/bin/etcd && mv /var/etcd/etcdctl /usr/local/bin/etcdctl
    # Etcd service file required at this path for starting service using systemctl

    echo "------+++++++++++"
    if [ $OPERATION_SYSTEM = "ubuntu" ];then
        if [ -d "/etc/systemd/system" ];then
            cp "$DIR"/etc/services-startup-conf/etcd.service /etc/systemd/system/etcd.service
            sed "s/\${CHUID}/$CURR_USER/"  "$DIR"/etc/services-startup-conf/etcd.conf > /etc/init/etcd.conf
        fi
    elif [ $OPERATION_SYSTEM = "centos" ];then
        # TODO: support centos
        echo "------"
    fi
    start_etcd
}

function prepare_install_valence()
{
    CURR_USER="$(whoami)"
    if [ ! -d '/var/log/valence' ];then
        mkdir -p /var/log/valence
        chown $CURR_USER:$CURR_USER /var/log/valence
        touch /var/log/valence/valence_install.log
    fi
    if [ ! -d '/etc/valence/' ];then
        mkdir -p /etc/valence
        chown $CURR_USER:$CURR_USER /etc/valence/
    fi
    INSTALL_LOG=/var/log/valence/valence_install.log
    echo "Current directory: $DIR" >> $INSTALL_LOG
}

function install_valence()
{
    pip install -r requirements.txt
    python setup.py install
    if [ $? -ne 0 ]; then
        echo "ERROR: setup.py failed. Please check /var/log/valence/INSTALL_LOG for details.
              Please fix the error and retry."
        exit
    fi

    if [ $OPERATION_SYSTEM = "ubuntu" ];then
        if [ -d "/etc/systemd/system" ]; then
            cp "$DIR"/etc/services-startup-conf/valence.service /etc/systemd/system/valence.service
        fi
    elif [ $OPERATION_SYSTEM = "centos" ];then
        # TODO: support centos
        echo ""
    fi

}

function config_valence()
{
    pip install tox
    echo "It will take few minites to generate configuration file by tox tool, please be patient!!!"
    tox -egenconfig
    VALENCE_CONF=/etc/valence/valence.conf
    cp "$DIR"/etc/valence.conf.sample /etc/valence/valence.conf
    chown $CURR_USER:$CURR_USER /etc/valence/
    sudo sed -i "s/#debug\s*=.*/debug=true/" $VALENCE_CONF
    sudo sed -i "s/#log_level\s*=.*/log_level=debug/" $VALENCE_CONF
    sudo sed -i "s/#log_file\s*=.*/log_file=\/var\/log\/valence\/valence.log/" $VALENCE_CONF
    sudo sed -i "s/#bind_host\s*=.*/bind_host=0.0.0.0/" $VALENCE_CONF
    sudo sed -i "s/#bind_port\s*=.*/bind_port=8181/" $VALENCE_CONF
    sudo sed -i "s/#timeout\s*=.*/timeout=1000/" $VALENCE_CONF
    sudo sed -i "s/#workers\s*=.*/workers=4/" $VALENCE_CONF
    sudo sed -i "s/#host\s*=.*/host=localhost/" $VALENCE_CONF
    sudo sed -i "s/#port\s*=.*/port=2379/" $VALENCE_CONF
}


install_dependency_package
install_etcd
prepare_install_valence
install_valence
config_valence
