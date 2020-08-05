# csss-site


 - [Setup Python Environment](#setup-python-environment)
 - [Setting the Necessary Environment Variables](#setting-the-necessary-environment-variables)
 - [Before opening a PR](#before-opening-a-pr)
 - [Various tasks to accomplish](#various-tasks-to-accomplish)


## Setup Python Environment
```shell
sudo apt-get install -y python3.7
sudo apt-get install python3-distutils --reinstall
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.7 get-pip.py --user
python3.7 -m pip install virtualenv --user
python3.7 -m virtualenv envCSSS
. envCSSS/bin/activate
git clone https://github.com/CSSS/csss-site.git
cd csss-site
python3.7 -m pip install -r requirements.txt
```


## Setting the Necessary Environment Variables  
> want to know why the weird way of quotes are used? -> https://stackoverflow.com/a/1250279/7734535  
```shell
echo 'BASE_DIR='"'"'<folder that contains csss-site repo>'"'"'' > CI/validate_and_deploy/site_envs
echo 'WEBSITE_SECRET_KEY='"'"'https://miniwebtool.com/django-secret-key-generator/'"'"'' >> CI/validate_and_deploy/site_envs
echo 'DEBUG='"'"'true'"'"'' >> CI/validate_and_deploy/site_envs
echo 'HOST_ADDRESS='"'"'<serverIP>>'"'"'' >> CI/validate_and_deploy/site_envs

# database configuration
if (you do not want to spin up a docker database){
    echo 'DB_TYPE='"'"'sqlite3'"'"'' >> CI/validate_and_deploy/site_envs
}else{
    echo 'DB_TYPE='"'"'postgres'"'"'' >> CI/validate_and_deploy/site_envs
    echo 'DB_PASSWORD='"'"'test_password'"'"'' >> CI/validate_and_deploy/site_envs
    echo 'DB_NAME='"'"'csss_website_db'"'"'' >> CI/validate_and_deploy/site_envs
    echo 'DB_PORT='"'"'5432'"'"'' >> CI/validate_and_deploy/site_envs
}

. CI/validate_and_deploy/set_env.sh site_envs

if (you choose to use a dockerized database){
    docker run --name ${DB_NAME} -p ${DB_PORT}:5432 -it -d -e POSTGRES_PASSWORD=${DB_PASSWORD} postgres:alpine
}

mkdir -p /path/to/csss-site/csss-site/src/logs

cd csss-site/src

../../CI/validate_and_deploy/migrate_apps.sh

python3.7 manage.py createsuperuser # if you need to log into the admin

python3.7 manage.py runserver 0.0.0.0:8000
```

## Before opening a PR
```shell
cd /absolute/path/to/parent/folder/of/repo
./CI/validate_and_deploy/test_site.sh
```

## Various tasks to accomplish

 * [Add frosh page for a new year](documentation/add_frosh.md)