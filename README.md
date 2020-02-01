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
cd csss-site-in-dev/


python3.7 -m pip install -r requirements.txt
cd csss
ifconfig
export ip_addr='serverIP'
export SECRET_KEY=`https://miniwebtool.com/django-secret-key-generator/`
docker run --name csss_site_db -p 5432:5432 -it -d -e POSTGRES_PASSWORD=test_password postgres:alpine
python3.7 manage.py migrate
python3.7 manage.py makemigrations
python3.7 manage.py migrate
python3.7 manage.py makemigrations elections
python3.7 manage.py migrate

python3.7 manage.py createsuperuser

python3.7 manage.py runserver 0.0.0.0:8000
```
