#!/usr/bin/env bash
set -o errexit

conda env create -f environment.yml

source activate django-gis

python manage.py collectstatic --no-input

python manage.py migrate