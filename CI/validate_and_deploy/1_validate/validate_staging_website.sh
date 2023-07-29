#!/bin/bash

# PURPOSE: used by jenkins to run the code on the dev.sfucsss.org past w3c

set -e -o xtrace

docker_test_image_lower_case=$(echo "$DOCKER_TEST_IMAGE" | awk '{print tolower($0)}')

docker rm -f ${DOCKER_TEST_CONTAINER} || true
docker image rm -f ${docker_test_image_lower_case} || true

rm -r ${BUILD_NUMBER}/${LOCALHOST_W3C_VALIDATION_TEST_DIR} || true
mkdir -p ${BUILD_NUMBER}/${LOCALHOST_W3C_VALIDATION_TEST_DIR}

docker build --no-cache -t ${docker_test_image_lower_case} \
    -f CI/validate_and_deploy/1_validate/Dockerfile.w3c_test \
    --build-arg CONTAINER_HOME_DIR=${CONTAINER_HOME_DIR} \
    --build-arg LOG_LOCATION=${CONTAINER_HOME_LOGS_DIR} \
    --build-arg TEST_RESULT_DIRECTORY=${CONTAINER_TEST_RESULT_DIRECTORY} .

echo "TEST_RESULT_DIRECTORY=${CONTAINER_TEST_RESULT_DIRECTORY}" > ${BUILD_NUMBER}/css_site_w3c_validation.env
echo "W3C_TESTS_URL=${W3C_TESTS_URL}" >> ${BUILD_NUMBER}/css_site_w3c_validation.env

sleep 120
docker run -d --name ${DOCKER_TEST_CONTAINER} --env-file ${BUILD_NUMBER}/css_site_w3c_validation.env ${docker_test_image_lower_case}

while [ "$(docker inspect -f '{{.State.Running}}' ${DOCKER_TEST_CONTAINER})" == "true" ]
do
	echo "waiting for the W3C validation to finish"
	sleep 1
done


docker cp ${DOCKER_TEST_CONTAINER}:${CONTAINER_TEST_RESULT_DIRECTORY}/xml/tests.xml \
    ${BUILD_NUMBER}/${LOCALHOST_W3C_VALIDATION_TEST_DIR}/${LOCALHOST_W3C_VALIDATION_XML_FILE_NAME}

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
