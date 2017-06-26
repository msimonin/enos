#!/usr/bin/env bash
set -x
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

cd $SCRIPT_DIR/packer_templates
tar -cf scripts/enos.tar\
  --exclude="*packer_cache*"\
  --exclude="*.iso"\
  --exclude="*qcow2"\
  --exclude=".git"\
  --exclude="*.tar"\
  ../../../..

kolla_ref=$(grep kolla_ref ../reservation.yaml | cut -d':' -f2 |xargs echo|sed 's$/$-$g')

# Making sure kvm will not conflict
#rmmod kvm-intel
PACKER_LOG=1 $SCRIPT_DIR/packer build -only virtualbox-iso -var "kolla_ref=$kolla_ref" debian-8.8-amd64.json

#modprobe kvm-intel
PACKER_LOG=1 $SCRIPT_DIR/packer build -only qemu -var "kolla_ref=$kolla_ref" debian-8.8-amd64.json
