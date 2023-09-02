# csss-site


 - [1. Setup Python Environment](#1-setup-python-environment)
 - [2. Setup and Run Website](#2-setup-and-run-website)
 - [3. Before opening a PR](#3-before-opening-a-pr)
 - [Various tasks to accomplish](#various-tasks-to-accomplish)


## 1. Setup Python Environment
### for Debian based OS
```shell
sudo apt-get install -y python3.9
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.7 get-pip.py --user
python3.7 -m pip install virtualenv --user
python3.7 -m virtualenv envCSSS
. envCSSS/bin/activate
```

### for MacOS
https://www.python.org/downloads/release/python-3913/
```shell
python3.9 -m pip install --upgrade pip
python3.9 -m pip install virtualenv
python3.9 -m virtualenv walle
. walle/bin/activate
```

### for Windows
open to anyone to make a PR adding this section

## 2. Setup and Run Website
```
If you hve not cloned your forked version yet
wget https://raw.githubusercontent.com/CSSS/csss-site/master/download_repo.sh
./download_repo.sh

If you have forked your version
./run_site.sh
```

## 3. Before opening a PR

**Please submit PRs one week before they need to be merged.**

## 3.1. Validating the code
```shell
../../CI/validate_and_deploy/1_validate/run_local_formatting_test.sh
```

## Various tasks to accomplish

[Link to wki for adding a webpage](https://github.com/CSSS/csss-site/wiki/Adding-a-Webpage)
