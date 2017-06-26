#!/usr/bin/env bash

set -xe

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# common steps
$SCRIPT_DIR/common_deps.sh

cp $SCRIPT_DIR/topology.yaml reservation.yaml

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

python -m enos.enos up &&\
python -m enos.enos info &&\
python -m enos.enos tc &&\
python -m enos.enos tc --test

# TODO: get the results and check their correctness
cat current/*.out &&\
cat current/*.stats
