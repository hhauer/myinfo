from django.conf.urls import url

from AccountPickup import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'aup/$', views.aup, name='aup'),
    url(r'odin/$', views.odin_name, name='odin'),
    url(r'alias/$', views.email_alias, name='alias'),
    url(r'contact/$', views.contact_info, name='contact_info'),
    url(r'next/$', views.oam_status_router, name='next_step'),
    url(r'wait/$', views.wait_for_provisioning, name='wait_for_provisioning'),
]