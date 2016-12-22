#!/usr/bin/env bash

eval $( aws ecr get-login )
bash dockerize-api.sh && bash docker-push-api.sh && bash deploy-to-eb.sh
cd ../inskop_ui && bash dockerize-ui.sh && bash docker-push-ui.sh && bash deploy-to-eb.sh
cd ../inskop_api