from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^MyInfo/', include('MyInfo.urls', namespace='MyInfo')),
    url(r'^AccountPickup/', include('AccountPickup.urls', namespace='AccountPickup')),
    url(r'^PasswordReset/', include('PasswordReset.urls', namespace='PasswordReset')),
    
    url(r'^accounts/login/$', 'django_cas.views.login', name='CASLogin'),
    url(r'^accounts/logout/$', 'django_cas.views.logout', name='CASLogout'),
    
    url(r'^ajax/', include('ajax.urls')),
    
    url(r'^admin/', include(admin.site.urls))
)
