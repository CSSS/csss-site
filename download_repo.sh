#!/bin/bash

set -e

echo "Please enter the HTTPS clone URL for your forked repo"
read forked_repo_https_clone_url
while [ "${forked_repo_https_clone_url}" == "https://github.com/CSSS/csss-site.git" ];
do
  echo "This is not a forked REPO url...Please enter the HTTPS clone URL for your forked repo"
  read forked_repo_https_clone_url
done

git clone "${forked_repo_https_clone_url}"
cd csss-site/
./run_site.sh