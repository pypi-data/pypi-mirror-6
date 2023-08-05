django-group-user-mngt
======================

Manage groups and users using jquery jtable

settings.py
-----------

Add to INSTALLED_APPS : 'group_user_mngt',

GROUP_MANAGEMENT_TEMPLATE = 'manage_groups.html'

Replace the templace with a customized template

urls.py
-------

url(r'^groupmanagement/', include('group_user_mngt.urls', namespace="gm_space")),

copy following files
--------------------

Under static root :

mkdir group_user_mngt 
cd group_user_mngt 
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/group_user_mngt/* .

under the static root (jtable dependencies)

mkdir js
cd js
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/js/* .
cd ..

mkdir css
cd css
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/css/* .
cd ..

Group view 
----------
http://<FQDN>/groupmanagement/group/update/

Future work
-----------

- CSRF support
- View with User as parent and group as child
- Edit permissions
- Improve portability of app
- ...

