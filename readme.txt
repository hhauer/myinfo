# Installation on RHEL6 
1) cd /var/www
2) virtualenv --no-site-packages myinfo
3) cd myinfo
4) git clone myinfo
5) git clone myinfo-config
6) cd myinfo/oam_base
7) ln -s /var/www/myinfo/myinfo-config/settings(?) ./

8) Edit manage.py to point to the correct settings file.
9) Download oracle instant client and SDK headers.
10) Unzip oracle parts into /var/www/myinfo
--  In the instant client folder ln -s libclntsh.so.11.1 to libclntsh.so
--  /etc/profile.d/oracle.sh for ORACLE_HOME var. (See wash)
11) Update /etc/sysconfig/httpd to set ORACLE_HOME and LD_LIBRARY_PATH to include oracle.
12) Activate python virtualenv.
13) Install requirements file.
14) Manually install cx_oracle with pip.
15) Reboot httpd.

16) [If necessary] create /var/log/myinfo.log and chown to myinfo:myinfo.

# Preparing the database
1) Remove initial_data.json from the myinfo project folder.
2) Run './manage.py syncdb' to create initial tables.
3) Run './manage.py createcachetable CACHE_TABLE' to build the DB cache.
4) Run './manage.py collectstatic' to build static files directory.

5) Eventually run './manage.py createsuperuser' to create first admin user.
* Username is a PSU_UUID as per the sailpoint instance MyInfo is pointing at.


###
# Sample apache config for myinfo.
# WSGI Config
WSGIScriptAlias / /var/www/myinfo/myinfo/oam_base/wsgi.py
WSGIDaemonProcess myinfo python-path=/var/www/myinfo/myinfo-env:/var/www/myinfo/lib/python2.6/site-packages user=myinfo group=myinfo
WSGIProcessGroup myinfo

<Directory /var/www/myinfo/psu-myinfo/PSU_MyInfo>
<Files wsgi.py>
Order allow,deny
Allow from all
</Files>
</Directory>

# Django Static Config
Alias /static/ /var/www/html/static/

<Directory /var/www/html/static>
Order deny,allow
Allow from all
</Directory>


============================= VAGRANT ===========================

In order to ease the setup of an appropriate dev environment for MyInfo a Vagrantfile and bootstrap.sh file are included.
First install Vagrant if it is not already available on the development system, then in an appropriate terminal / shell / command window
change to the PSU_MyInfo root directory and run "vagrant up" which will start the vagrant VM. On windows it may be necessary to open the VirtualBox
command window so that vagrant doesn't try to write its vm files to the H: drive.

Once vagrant has booted fully MyInfo will be available at 127.0.0.1:8000/MyInfo/

SSH to the vagrant server is available at 127.0.0.1:2222 with username vagrant and password vagrant. The PSU_MyInfo root directory is mapped to /vagrant
in the VM. If for some reason you need to manually start Django's server with the runserver command, be sure to use 0.0.0.0:8000 so that it will accept
pass-through connections from the host machine.
