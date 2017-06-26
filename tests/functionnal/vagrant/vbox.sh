#!/usr/bin/env bash

set -xe

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# common steps
$SCRIPT_DIR/common_deps.sh

cp $SCRIPT_DIR/vbox.yaml reservation.yaml

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

python -m enos.enos up &&\
python -m enos.enos os &&\
python -m enos.enos init &&\
python -m enos.enos destroy
