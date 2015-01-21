from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy

from MyInfo import views as my_info_views
from django_cas import views as cas_views
from oam_base import views as base_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', my_info_views.index, name='index'),
    url(r'^MyInfo/', include('MyInfo.urls', namespace='MyInfo')),
    url(r'^AccountPickup/', include('AccountPickup.urls', namespace='AccountPickup')),
    url(r'^PasswordReset/', include('PasswordReset.urls', namespace='PasswordReset')),

    url(r'^accounts/login/$', cas_views.login, {'next_page': reverse_lazy('AccountPickup:next_step')}, name='CASLogin'),
    url(r'^accounts/logout/$', cas_views.logout, name='CASLogout'),

    url(r'^error/denied$', base_views.rate_limited, name='rate_limited'),

    url(r'^ajax/', include('ajax.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

handler500 = 'oam_base.views.custom_error'