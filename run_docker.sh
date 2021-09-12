#!/bin/bash
export WORKSPACE=$PWD

if [ -n "$1" ]; then
    docker_image=$1
else
    docker_image="ikeabot:latest"
fi
echo "Running" $docker_image

docker run -it -w $WORKSPACE -v $WORKSPACE:$WORKSPACE  --network="host" $docker_image
