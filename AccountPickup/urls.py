from django.conf.urls import patterns, url

from AccountPickup import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'AUP/$', views.AUP, name='AUP'),
    url(r'ODIN/$', views.odinName, name='ODIN'),
    url(r'PasswordReset/$', views.password_reset, name='PasswordReset'),
)