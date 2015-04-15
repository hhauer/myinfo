from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from MyInfo import views as my_info_views
from django_cas import views as cas_views
from oam_base import views as base_views
from Duo import views as duo_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', my_info_views.index, name='index'),
    url(r'^MyInfo/', include('MyInfo.urls', namespace='MyInfo')),
    url(r'^AccountPickup/', include('AccountPickup.urls', namespace='AccountPickup')),
    url(r'^PasswordReset/', include('PasswordReset.urls', namespace='PasswordReset')),

    url(r'^accounts/login/$', cas_views.login, {'next_page': reverse_lazy('AccountPickup:next_step')}, name='CASLogin'),
    url(r'^duo/login/$', cas_views.login, name='duoLogin'),
    url(r'^accounts/logout/$', cas_views.logout, name='CASLogout'),

    url(r'^status/denied/$', base_views.rate_limited, name='rate_limited'),

    url(r'^ajax/', include('ajax.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Simple redirects for static files that browsers expect to be at the root.
    url(r'^robots\.txt$', RedirectView.as_view(url='/static/robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),

    url(r'^duo$', duo_views.login,name='duo_login')
)

handler500 = 'oam_base.views.custom_error'