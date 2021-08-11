#!/bin/bash

set -e -o xtrace

mkdir -p ../../media_root
pushd ../../media_root/
wget -r --no-host-directories https://dev.sfucsss.org/mailbox_attachments/ -R '*html*'
popd