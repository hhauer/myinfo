from django.conf.urls import patterns, url

from MyInfo import views

urlpatterns = patterns('',
    url(r'pick_action/$', views.pick_action, name='pick_action'),
    url(r'set_password/$', views.set_password, name='set_password'),
    url(r'set_directory/$', views.set_directory, name='set_directory'),
    url(r'set_contact/$', views.set_contact, name='set_contact'),
    url(r'welcome/$', views.welcome_landing, name='welcome_landing'),
)