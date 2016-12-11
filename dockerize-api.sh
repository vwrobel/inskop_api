#!/usr/bin/env bash

docker build -t inskop_api -t 939102736904.dkr.ecr.eu-west-1.amazonaws.com/inskop_api:latest ./api
docker build -t inskop_api_nginx -t 939102736904.dkr.ecr.eu-west-1.amazonaws.com/inskop_api_nginx:latest ./nginx
