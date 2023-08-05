from distutils.core import setup

setup(
    name = 'django-group-user-mngt',
    packages = ['group_user_mngt'],
    version = '0.9',
    #include_package_data=True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        'group_user_mngt': [
            'templates/*',
            'static/group_user_mngt/*',
            'static/css/jtable/*.css',
            'static/css/jtable/images/*',
            'static/js/jtable/*',
            ],
    },

    description = 'Manage groups and user via jtable',
    author = 'Erwin Sprengers',
    author_email = 'sprengee54@gmail.com',
    url = 'http://pypi.python.org/pypi//django-group-user-mngt',   # use the URL to the github repo
    keywords = ['django', 'admin', 'user', 'group', ], # arbitrary keywords
    classifiers = [],
)
