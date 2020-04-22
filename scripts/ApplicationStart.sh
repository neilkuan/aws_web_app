#!/bin/bash
docker run -p 80:5000 --name flask-devops -d guanyebo/web-app:v1
exit 0
