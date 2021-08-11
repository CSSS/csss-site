#!/bin/bash

set -e -o xtrace

pushd about/static/about_static/
rm -fr exec-photos || true
wget -r --no-host-directories https://dev.sfucsss.org/exec-photos/ -R '*html*'
popd