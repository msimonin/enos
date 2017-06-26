#!/usr/bin/env bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
version=0.12.2

apt-get -y update
# install vagrant
wget https://releases.hashicorp.com/vagrant/1.9.6/vagrant_1.9.6_x86_64.deb -O vagrant.deb
dpkg -i vagrant.deb
apt-get -f -y  install
# install vbox
wget http://download.virtualbox.org/virtualbox/5.1.22/virtualbox-5.1_5.1.22-115126~Debian~jessie_amd64.deb -O vbox.deb
dpkg -i vbox.deb
apt-get -f -y  install
# install packer
cd $SCRIPT_DIR
wget https://releases.hashicorp.com/packer/${version}/packer_${version}_linux_amd64.zip
unzip packer_${version}_linux_amd64.zip
