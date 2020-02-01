#!/bin/bash


apps_to_migrate=($(ls -1 ./))
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
