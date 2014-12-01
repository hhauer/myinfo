from django.conf.urls import patterns, url

from PasswordReset import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'reset/(?P<token>[-:\w]+)/$', views.reset, name='reset'),
    url(r'reset/$', views.reset, name='reset_notoken'),
    #url(r'AUP/$', views.AUP, name='AUP'),
)
