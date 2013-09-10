#!/usr/bin/env bash

apt-get update
apt-get install -y python python-pip vim elinks sqlite3
pip install -r /vagrant/requirements.txt
cp /vagrant/secure_settings.ini /home/vagrant/secure_settings.ini
python /vagrant/manage.py syncdb --noinput
python /vagrant/manage.py loaddata /vagrant/initial_data.json
python /vagrant/manage.py runserver 0.0.0.0:8000 &