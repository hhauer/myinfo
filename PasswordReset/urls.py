from django.conf.urls import url

from PasswordReset import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'reset/(?P<token>[-:\w]+)/$', views.reset, name='reset'),
    url(r'reset/$', views.reset, name='reset_notoken'),
]
