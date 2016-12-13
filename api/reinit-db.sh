#!/usr/bin/env bash

python manage.py flush
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata ./inskop/account_manager/fixtures/account_data.yaml
python manage.py loaddata ./inskop/other_manager/fixtures/other_data.yaml
python manage.py loaddata ./inskop/code_manager/fixtures/code_data.yaml
python manage.py loaddata ./inskop/scene_manager/fixtures/scene_data.yaml
python manage.py cvtools_to_codes