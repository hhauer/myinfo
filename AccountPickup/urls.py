from django.conf.urls import patterns, url

from AccountPickup import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'aup/$', views.AUP, name='aup'),
    url(r'odin/$', views.odinName, name='odin'),
    url(r'alias/$', views.email_alias, name='alias'),
    url(r'contact/$', views.contact_info, name='contact_info'),
    url(r'next/$', views.oam_status_router, name='next_step'),
    url(r'wait/$', views.wait_for_provisioning, name='wait_for_provisioning'),
    url(r'complete/$', views.provisioning_complete, name='provisioning_complete'),
)