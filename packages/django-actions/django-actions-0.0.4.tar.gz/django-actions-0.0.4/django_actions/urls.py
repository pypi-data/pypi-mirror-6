from django.conf.urls import patterns, url
from .views import index, do

urlpatterns = patterns(
    '',
    url(r'do/(?P<action_name_slugified>[\w-]+)/$', do, name='do_action'),
    url(r'$', index, name='django_actions_index'),
)
