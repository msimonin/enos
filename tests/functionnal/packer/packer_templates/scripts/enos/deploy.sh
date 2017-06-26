#!/bin/sh -x
# NOTE(msimonin): -u won't work to _OLD_PYTHON_PATH unset when calling
# the first time activate
BUILD_DIR=$HOME/enos

cd $BUILD_DIR
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

cp tests/functionnal/packer/reservation.yaml .
python -m enos.enos deploy && python -m enos.enos destroy
