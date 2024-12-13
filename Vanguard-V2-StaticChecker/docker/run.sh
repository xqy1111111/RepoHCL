#!/bin/bash

docker container prune -f
docker image prune -f

docker build -f docker/dockerfile.cg -t cg .
docker build -f docker/dockerfile.cg_libxml2 -t cg_libxml .

docker run -td cg_libxml bash
container_id=$(docker ps | grep 'cg_libxml' | awk '{print $1}')
docker cp ${container_id}:/root/output/cg.dot ../output/
docker cp ${container_id}:/root/output/functions.json ../output/
docker cp ${container_id}:/root/vanguard/cmake-build-debug/tools/CallGraphGen/cge ../lib/
docker stop ${container_id}

#docker build --no-cache -f docker/dockerfile.cg_vanguard -t cg_vanguard .
#docker run -td cg_vanguard bash
#container_id=$(docker ps | grep 'cg_vanguard' | awk '{print $1}')
#docker cp ${container_id}:/root/output/cg.dot ../output/
#docker cp ${container_id}:/root/output/functions.json ../output/
#docker stop ${container_id}