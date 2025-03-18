#!/bin/bash

# source docker/run.sh <lib>
# example: source docker/run.sh pugixml

docker container prune -f
docker image prune -f

docker build -f docker/dockerfile.cg -t cg .
docker build -f docker/dockerfile.cg_"$1" -t cg_"$1" --network=host .

docker run -td cg_"$1" bash

container_id=$(docker ps | grep "cg_$1" | awk '{print $1}')
mkdir -p ../output/"${1}"
docker cp "${container_id}":/root/output/cg.dot ../output/"${1}"
docker cp "${container_id}":/root/output/functions.json ../output/"${1}"/
docker cp "${container_id}":/root/output/structs.json ../output/"${1}"/
docker cp "${container_id}":/root/output/records.json ../output/"${1}"/
docker cp "${container_id}":/root/output/typedefs.json ../output/"${1}"/
docker cp "${container_id}":/root/vanguard/cmake-build-debug/tools/CallGraphGen/cge ../lib/
docker stop "${container_id}"