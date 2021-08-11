# csss-site


 - [1. Setup Python Environment](#1-setup-python-environment)
 - [2. Setting the Necessary Environment Variables](#2-setting-the-necessary-environment-variables)
 - [Before opening a PR](#3-before-opening-a-pr)
 - [Various tasks to accomplish](#various-tasks-to-accomplish)


## 1. Setup Python Environment
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


## 2. Setting the Necessary Environment Variables  
> want to know why the weird way of quotes are used? -> https://stackoverflow.com/a/1250279/7734535  
```shell
echo 'BASE_DIR='"'"'<folder that contains csss-site repo>'"'"'' > CI/validate_and_deploy/2_deploy/site_envs
echo 'WEBSITE_SECRET_KEY='"'"'https://miniwebtool.com/django-secret-key-generator/'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
echo 'DEBUG='"'"'true'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
echo 'HOST_ADDRESS='"'"'<serverIP>'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
echo 'ENVIRONMENT='"'"'LOCALHOST'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
echo 'PORT='"'"'8000'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
echo 'DB_CONTAINER_NAME='"'"'csss_website_dev_db'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
if (you do not want to spin up a docker database){
    echo 'DB_TYPE='"'"'sqlite3'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
}else{
    echo 'DB_TYPE='"'"'postgres'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
    echo 'DB_PASSWORD='"'"'test_password'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
    echo 'DB_NAME='"'"'csss_website_db'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
    echo 'DB_PORT='"'"'5432'"'"'' >> CI/validate_and_deploy/2_deploy/site_envs
}
```

### 2.1 Set Environment Variables
```shell
cd csss-site/src
. ../../CI/validate_and_deploy/2_deploy/set_env.sh site_envs
```

### 2.2 Create log folder
```shell
mkdir -p /path/to/csss-site/website_logs/python_logs
```

### 2.3 Spin up Dockerized Database and Setup Database Entries
```shell
if (you choose to use a dockerized database){
    sudo apt-get install postgresql-contrib
    ../../CI/fixtures_and_media_download/create_dockerized_database_with_migration.sh
    git checkout <your_branch_name>
}else{
    ../../CI/fixtures_and_media_download/create_sqlite_database_with_migration.sh
}
```

### 2.4 Set up Announcement Attachments
```shell
if (you want to downlaod the attachments from the staging server){
  ../../CI/fixtures_and_media_download/download_mailbox_attachments.sh
}else{
  python3 manage.py create_attachments
}
```

### 2.5 Set up Officer Profile Pics
```shell
if (you want to use the actual images instead of the stock photos){
  ../../CI/fixtures_and_media_download/download_officer_photos.sh
}
python3 manage.py update_officer_images
```


### 2.6 Needed if you need to log into /admin
```shell
python3 manage.py createsuperuser
```

### 2.7 Run Site
```shell
python3 manage.py runserver 0.0.0.0:8000
```

## 3. Before opening a PR

## 3.1. Validating the code
```shell
../../CI/validate_and_deploy/1_validate/run_local_formatting_test.sh
```

## Various tasks to accomplish

 * [Add an events page for frosh, mountain madness, or fall hacks for a new year](documentation/Add_An_Event.md)
