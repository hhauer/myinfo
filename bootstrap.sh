#!/usr/bin/env bash

apt-get update
apt-get install -y python python-pip vim sqlite3
pip install -r /vagrant/requirements.txt
rm -f /vagrant/sqlite.db
python /vagrant/manage.py syncdb --noinput
nohup python /vagrant/manage.py runserver 0.0.0.0:8000
