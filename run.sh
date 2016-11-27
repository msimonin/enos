#!/usr/bin/env bash

python -m enos.enos deploy --force-deploy
shaker-image-builder --external-net public --image-builder-template ubuntu.yaml;
shaker --server-endpoint 172.16.111.106:4445 --scenario dense_l2.yaml  --external-net provider --report current/shaker_report.html --book current/shaker_report
python -m enos.enos backup
