#!/bin/bash


apps_to_migrate=($(ls -1 ./))
python3 manage.py migrate
yes | python3 manage.py makemigrations
yes | python3 manage.py migrate

for app_to_migrate in "${apps_to_migrate[@]}"
do
   :
   echo "migrating ${app_to_migrate}"
   yes | python3 manage.py makemigrations ${app_to_migrate}
   yes | python3 manage.py migrate
done
