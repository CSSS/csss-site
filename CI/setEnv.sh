#!/bin/bash

ENV_FILE=$1

if [ "$#" -eq 0 ]
then
    echo "please provide the name used for the env variable file"
    exit 1
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -o allexport
source "${DIR}"/"${ENV_FILE}"
set +o allexport
