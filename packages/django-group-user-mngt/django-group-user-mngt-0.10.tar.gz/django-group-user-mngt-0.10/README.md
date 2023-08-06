django-group-user-mngt
======================

Manage django native groups and users tables using jquery jtable.  Two possible views are foreseen.  The first view is listing all the user as
master table and the groups as child table.  The second view have the groups listed and the users in the child table.
Create/delete action of child record have rather the sematics of linking/unlinking items.

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

The dist-packages subdirectory in the examples below is just an example.  It all depends on
how this package was installed (with or without env, ubuntu/windows, ...)

Under your project static root :

mkdir group_user_mngt
cd group_user_mngt
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/group_user_mngt/* .

under your project static root (jtable dependencies)

mkdir js
cd js
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/js/* .
cd ..

mkdir css
cd css
cp -r /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/css/* .
cd ..

mkdir group_user_mngt
cd group_user_mngt
cp /usr/local/lib/python2.7/dist-packages/group_user_mngt/static/group_user_mngt/* .

Group view
----------

http://<FQDN>/groupmanagement/group/update/

Future work
-----------

- CSRF support
- Edit permissions
- Improve portability of app
- ...

