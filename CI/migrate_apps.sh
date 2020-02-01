#!/bin/bash


if [ "$#" -eq 0 ]
then
    echo "please provide the absolute path location of the django apps"
    exit 1
fi

ENV_FILE=$1

apps_to_migrate=($(ls -1 ${ENV_FILE}))
python3.7 manage.py migrate
python3.7 manage.py makemigrations
python3.7 manage.py migrate

for app_to_migrate in "${apps_to_migrate[@]}"
do
   :
   echo "migrating ${app_to_migrate}"
   python3.7 manage.py makemigrations ${app_to_migrate}
   python3.7 manage.py migrate
done
