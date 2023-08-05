from django.conf.urls import patterns, url
from views import ajax_render

urlpatterns = patterns('',
              url(r'^async_text/(?P<plugin_id>\d+)/$', ajax_render,
                  name = 'ajax_render')
              )
