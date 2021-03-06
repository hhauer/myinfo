from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from MyInfo import views


urlpatterns = [
    url(r'pick_action/$', login_required(TemplateView.as_view(template_name="MyInfo/pick_action.html"),
                                         login_url=reverse_lazy('index')), name='pick_action'),
    url(r'set_password/$', views.set_password, name='set_password'),
    url(r'set_directory/$', views.DirectoryView.as_view(), name='set_directory'),
    url(r'set_contact/$', views.set_contact, name='set_contact'),
    url(r'welcome/$', views.welcome_landing, name='welcome_landing'),

    url(r'ping/$', views.ping, name='ping'),
]
