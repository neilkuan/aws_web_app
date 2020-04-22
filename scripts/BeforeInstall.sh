#!/bin/bash

# $(aws ecr get-login --no-include-email --registry-ids $aws-account-id --region ap-northeast-1)

if [ `docker images | grep web-app | wc -l`  = 1 ]
then
        docker rmi guanyebo/web-app:v1
        docker pull guanyebo/web-app:latest
else
        docker pull guanyebo/web-app:latest
fi
