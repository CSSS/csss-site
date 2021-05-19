#!/bin/bash


# PURPOSE: to be used by the user when they want to test their code against the linter

docker stop csss_website_test || true
docker rm csss_website_test || true
docker image rm csss_website_test || true
pushd ../../
docker build -t csss_website_test -f CI/validate_and_deploy/1_validate/Dockerfile.test \
 --build-arg CONTAINER_HOME_DIR=/usr/src/app --build-arg UNIT_TEST_RESULTS=/usr/src/app/tests \
  --build-arg TEST_RESULT_FILE_NAME=all-unit-tests.xml .
popd
docker run -d --name csss_website_test csss_website_test


while [ "$(docker inspect -f '{{.State.Running}}' csss_website_test)"  = "true" ]
do
	echo "waiting for testing to complete"
	sleep 1
done

docker logs csss_website_test
