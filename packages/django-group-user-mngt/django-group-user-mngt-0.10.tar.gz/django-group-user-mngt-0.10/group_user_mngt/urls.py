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

from group_user_mngt.views import manage_users
from group_user_mngt.views import ajax_um_user_display
from group_user_mngt.views import ajax_um_group_display
from group_user_mngt.views import ajax_um_user_add
from group_user_mngt.views import ajax_um_user_delete
from group_user_mngt.views import ajax_um_user_update
from group_user_mngt.views import ajax_um_group_attach
from group_user_mngt.views import ajax_um_group_detach
from group_user_mngt.views import ajax_um_group_index

#admin.autodiscover()

'''
<div id="GroupUserMngt" class="grid_16">{% csrf_token %}</div>
'''
urlpatterns = patterns('',
    #Groups master - user slave view
    url(r'^group/update/$', manage_groups, name='update_group'),
    url(r'^ajax/group-m/display/$', ajax_gm_group_display),
    url(r'^ajax/user-s/display/(?P<gname>.*)$', ajax_gm_user_display),
    url(r'^ajax/group-m/update/$', ajax_gm_group_update),
    url(r'^ajax/group-m/delete/$', ajax_gm_group_delete),
    url(r'^ajax/group-m/add/$', ajax_gm_group_add),
    url(r'^ajax/user-s/add/(?P<gname>.*)$', ajax_gm_user_attach),
    url(r'^ajax/user-s/delete/(?P<gname>.*)$', ajax_gm_user_detach),
    url(r'^ajax/user-s/index/(?P<gname>.*)$', ajax_gm_user_index),
    #User master - group slave view
    url(r'^user/update/$', manage_users, name='update_user'),
    url(r'^ajax/user-m/display/$', ajax_um_user_display),
    url(r'^ajax/group-s/display/(?P<uname>.*)$', ajax_um_group_display),
    url(r'^ajax/user-m/update/$', ajax_um_user_update),
    url(r'^ajax/user-m/delete/$', ajax_um_user_delete),
    url(r'^ajax/user-m/add/$', ajax_um_user_add),
    url(r'^ajax/group-s/add/(?P<uname>.*)$', ajax_um_group_attach),
    url(r'^ajax/group-s/delete/(?P<uname>.*)$', ajax_um_group_detach),
    url(r'^ajax/group-s/index/(?P<uname>.*)$', ajax_um_group_index),

)

