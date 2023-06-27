#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -o allexport
source "${DIR}"/"csss_site.env"
set +o allexport
