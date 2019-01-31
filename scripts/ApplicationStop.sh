#!/bin/bash
if [ `docker ps | grep flask-devops | wc -l`  = 1 ]
then
        docker stop flask-devops
        docker rm  flask-devops
fi
