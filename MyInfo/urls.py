from django.conf.urls import patterns, url

from MyInfo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^set_password/$', views.set_password, name='set_password'),
    url(r'^set_directory/$', views.set_directory, name='set_directory'),
    url(r'^set_contact/$', views.set_contact, name='set_contact'),
)