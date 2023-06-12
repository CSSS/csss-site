#!/bin/bash

# PURPOSE: used by jenkins to run the code on the dev.sfucsss.org past w3c

set -e -o xtrace

docker_test_image_lower_case=$(echo "$DOCKER_TEST_IMAGE" | awk '{print tolower($0)}')

docker rm -f ${DOCKER_TEST_CONTAINER} || true
docker image rm -f ${docker_test_image_lower_case} || true

docker build --no-cache -t ${docker_test_image_lower_case} \
    -f CI/validate_and_deploy/1_validate/Dockerfile.w3c_test \
    --build-arg CONTAINER_HOME_DIR=${CONTAINER_HOME_DIR} \
    --build-arg LOG_LOCATION=${CONTAINER_HOME_LOGS_DIR} \
    --build-arg TEST_RESULT_DIRECTORY=${CONTAINER_TEST_RESULT_DIRECTORY} .

echo "TEST_RESULT_DIRECTORY=${CONTAINER_TEST_RESULT_DIRECTORY}" >> site_envs
echo "W3C_TESTS_URL=${W3C_TESTS_URL}" >> site_envs

sleep 120
docker run -d --name ${DOCKER_TEST_CONTAINER} --env-file site_envs ${docker_test_image_lower_case}

while [ "$(docker inspect -f '{{.State.Running}}' ${DOCKER_TEST_CONTAINER})" == "true" ]
do
	echo "waiting for the W3C validation to finish"
	sleep 1
done

rm -r ${LOCALHOST_TEST_DIR} || true

docker cp ${DOCKER_TEST_CONTAINER}:${CONTAINER_TEST_RESULT_DIRECTORY} \
    ${LOCALHOST_TEST_DIR}

test_container_failed=$(docker inspect ${DOCKER_TEST_CONTAINER} --format='{{.State.ExitCode}}')
if [ "${test_container_failed}" -eq "1" ]; then
    docker logs ${DOCKER_TEST_CONTAINER}
    docker stop ${DOCKER_TEST_CONTAINER} || true
    docker rm ${DOCKER_TEST_CONTAINER} || true
    docker image rm -f ${docker_test_image_lower_case} || true
    exit 1
fi

docker stop ${DOCKER_TEST_CONTAINER} || true
docker rm ${DOCKER_TEST_CONTAINER} || true
docker image rm -f ${docker_test_image_lower_case} || true
exit 0
