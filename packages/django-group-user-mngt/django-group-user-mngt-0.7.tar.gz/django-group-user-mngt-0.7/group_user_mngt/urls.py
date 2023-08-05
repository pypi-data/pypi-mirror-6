import sys

from django.conf.urls import patterns, include, url
from django.conf.urls import patterns, url

from group_user_mngt.views import manage_groups
from group_user_mngt.views import ajax_gm_group_display
from group_user_mngt.views import ajax_gm_user_display
from group_user_mngt.views import ajax_gm_group_add
from group_user_mngt.views import ajax_gm_group_delete
from group_user_mngt.views import ajax_gm_group_update
from group_user_mngt.views import ajax_gm_user_attach
from group_user_mngt.views import ajax_gm_user_detach
from group_user_mngt.views import ajax_gm_user_index

#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^group/update/$', manage_groups, name='update_group'),
    url(r'^ajax/group-m/display/$', ajax_gm_group_display),
    url(r'^ajax/user-s/display/(?P<gname>.*)$', ajax_gm_user_display),
    url(r'^ajax/group-m/update/$', ajax_gm_group_update),
    url(r'^ajax/group-m/delete/$', ajax_gm_group_delete),
    url(r'^ajax/group-m/add/$', ajax_gm_group_add),
    url(r'^ajax/user-s/add/(?P<gname>.*)$', ajax_gm_user_attach),
    url(r'^ajax/user-s/delete/(?P<gname>.*)$', ajax_gm_user_detach),
    url(r'^ajax/user-s/index/(?P<gname>.*)$', ajax_gm_user_index),


)

