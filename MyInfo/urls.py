from django.conf.urls import patterns, url

from MyInfo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^update_information/$', views.update_information, name='update')
)