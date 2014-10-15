# MyInfo: A User Self-Service Interface for SailPoint IIQ

Originally designed to support the needs of Portland State University, MyInfo is a user-facing portal for password management, password recovery, initial account provisioning, and more.

MyInfo is broken into three major pieces each handling a different part of the user experience.

### AccountPickup

New users are guided through the process of claiming their account using a construct similar to the concept of a "core router." As each requirement is met it is recorded in a per-user model. If the user leaves and comes back their current step in the process is remembered. The user is not allowed to go "back" as it is assumed that background provisioning tasks will be launched which have irrevocable consequences.

### MyInfo

Returning users have the opportunity to update their password, the information they use for password self-service resets, and if eligible their directory information.

### PasswordReset

Using an SMS-capable phone number or external email address the user is able to regain access to reset their password if they have forgotten their previous pattern. This functionality models similar functionality commonly seen from online service providers.

## Custom Modules

* In order to support the business needs of PSU this project embeds a custom fork of Django_CAS (originally from https://bitbucket.org/cpcc/django-cas/overview)
* longerusername is used to support 36-character usernames, a requirement of PSU's implementation.

### Installation

## Requirements

As MyInfo uses Django 1.7+, Python3 (preferable 3.3+) is required.

## Steps

1. Clone to directory of choice.
2. 'pip install -r requirements.txt'
2. './manage.py migrate'
3. './manage.py createcachetable'
5. './manage.py collectstatic'
6. Launch with WSGI-compatible server of choice.

## Vagrant

A vagrantfile and bootstrap.sh are provided as they have been used in the past to aid development of templates / interface elements by non-technical users, but have not been updated or maintained since the switch to Django 1.7 and Python3. They are provided primarily as a reference.

### Roadmap

Planned future changes:
* Genericize the password strength meter and fork into its own project.
* Simplify password reset to detect if SMS or email. Make all reset codes shortcodes.