#!/bin/bash

aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 338015061559.dkr.ecr.ap-southeast-1.amazonaws.com
docker build -t swv .
docker tag swv:latest 338015061559.dkr.ecr.ap-southeast-1.amazonaws.com/synapse-workvivo:latest
docker push 338015061559.dkr.ecr.ap-southeast-1.amazonaws.com/synapse-workvivo:latest