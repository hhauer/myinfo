To Install:

Clone the repository into /var/www/myinfo/psu-myinfo
Set up the virtualenv at /var/www/myinfo/myinfo-env
Use pip to install python requirements into the environment.

Create a user named "myinfo"
Put secure_settings.ini in the myinfo user's home directory.

Install the cx_Oracle 64-bit Centos5 for oracle 11g RPM.
Install the oracle 64-bit 11g instantclient RPM.
export ORACLE_HOME = /usr/lib/oracle/11.2/client64
sudo echo "/usr/lib/oracle/11.2/client64/lib" > /etc/ld.so.conf.d/oracle.conf
sudo ldconfig
(cx_Oracle is now working in global python.)
Copy the cx_Oracle.so out of the global python into the local environment. (As opposed to building from source, which is probably better but I never got it to work on my short deadline.)


# sudo execstack -c /usr/lib/oracle/11.2/client64/lib/libnnz11.so
# selinux /home/myinfo to allow httpd read.

Create /etc/httpd/conf.d/psu-myinfo.conf with the following:

============================= BELOW =============================
# WSGI Config
WSGIScriptAlias / /var/www/myinfo/psu-myinfo/PSU_MyInfo/wsgi.py
WSGIDaemonProcess psu-myinfo python-path=/var/www/myinfo/myinfo-env:/var/www/myinfo/psu-myinfo user=myinfo group=myinfo
WSGIProcessGroup psu-myinfo

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
============================= ABOVE =============================

-- Remove initial_data.json if not using vagrant for development. It will populate false data if left in place on a dev server.
-- Enable the python environment, then syncdb
-- The default admin username needs to be a PSU_UUID. If not readily available, replace it via SQLDeveloper.
-- Login to http://host/admin which should work via CAS. Add necessary data.

============================= VAGRANT ===========================

In order to ease the setup of an appropriate dev environment for MyInfo a Vagrantfile and bootstrap.sh file are included.
First install Vagrant if it is not already available on the development system, then in an appropriate terminal / shell / command window
change to the PSU_MyInfo root directory and run "vagrant up" which will start the vagrant VM. On windows it may be necessary to open the VirtualBox
command window so that vagrant doesn't try to write its vm files to the H: drive.

Once vagrant has booted fully MyInfo will be available at 127.0.0.1:8000/MyInfo/

SSH to the vagrant server is available at 127.0.0.1:2222 with username vagrant and password vagrant. The PSU_MyInfo root directory is mapped to /vagrant
in the VM. If for some reason you need to manually start Django's server with the runserver command, be sure to use 0.0.0.0:8000 so that it will accept
pass-through connections from the host machine.

As with all MyInfo configurations a secure_settings.ini file will need to be in the root directory before starting vagrant.