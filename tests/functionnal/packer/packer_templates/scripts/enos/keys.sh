#!/bin/sh -x

ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
cp -r /root/.ssh /home/vagrant/.
chown -R vagrant:vagrant /home/vagrant/.ssh
