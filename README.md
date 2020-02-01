# csss-site

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
ifconfig
# want to know why the wierd way of quotes are used? -> https://stackoverflow.com/a/1250279/7734535
echo 'BASE_DIR='"'"'<folder that contains csss-site repo>'"'"'' > CI/site_envs
echo 'SECRET_KEY='"'"'https://miniwebtool.com/django-secret-key-generator/'"'"'' >> CI/site_envs
echo 'DEBUG='"'"'true'"'"'' >> CI/site_envs
echo 'HOST_ADDRESS='"'"'<serverIP>>'"'"'' >> CI/site_envs

echo 'DB_TYPE='"'"'<sqlite3 or postgres>'"'"'' >> CI/site_envs
# if you do not want to spin up a docker database, use sqlite3

# below 2 are only needed if you decided to use sqlite3
echo 'DB_PASSWORD='"'"'test_password'"'"'' >> CI/site_envs
echo 'DB_PORT='"'"'5432'"'"'' >> CI/site_envs

. CI/setEnv.sh site_envs

docker run --name csss_site_db -p ${DB_PORT}:5432 -it -d -e POSTGRES_PASSWORD=${DB_PASSWORD} postgres:alpine

mkdir -p /path/to/csss-site/csss-site/src/logs

cd csss-site/src

../../CI/migrate_apps.sh

python3.7 manage.py createsuperuser # if you need to log into the admin

python3.7 manage.py runserver 0.0.0.0:8000
```


# Before opening a PR
```shell
cd /absolute/path/to/parent/folder/of/repo
./CI/test_site.sh
```
