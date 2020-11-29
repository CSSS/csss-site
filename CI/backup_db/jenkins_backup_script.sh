#!/bin/bash

scp CI/backup_db/backup.sh csss@"${HOST_ADDRESS}":"${BASE_DIR}/backup.sh"
ssh csss@"${HOST_ADDRESS}" "${BASE_DIR}/backup.sh";
ssh csss@"${HOST_ADDRESS}" "rm ${BASE_DIR}/backup.sh";