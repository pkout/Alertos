#!/bin/bash

# If the docker image for test isn't built yet, build it first.
if [ -z "$(docker images -q alertos_test:latest 2> /dev/null)" ]; then
    echo "Building test docker image"
    docker build -t alertos_test -f Dockerfile.test .
fi

echo "Running tests"
docker run --rm --name alertos_test --volume .:/code alertos_test /bin/bash -c "cd .. && ./run_unit_tests.sh $@"