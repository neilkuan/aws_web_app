#!/bin/bash
if [ `docker ps | grep cc104_devops | wc -l`  = 1 ]
then
        docker stop cc104_devops
        docker rm  cc104_devops
fi
