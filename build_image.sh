#!/usr/bin/env bash
# build the image
docker build -t artuszkrol/kilimanjarovr:frontend .
# push image to docker hub
docker push artuszkrol/kilimanjarovr:frontend