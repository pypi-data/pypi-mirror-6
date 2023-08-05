CMSPlugin Frequently
====================

django-cms plugin and apphook for the django-frequently app.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install cmsplugin-frequently

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/cmsplugin-frequently.git#egg=cmsplugin_frequently

TODO: Describe further installation steps (edit / remove the examples below):

Add ``cmsplugin_frequently`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'cmsplugin_frequently',
    )

If you are a new user, migrate your database. If you used django-frequently<2.0
before, skip this step and follow the steps below.

.. code-block:: bash

    ./manage.py migrate cmsplugin_frequently

Migration from django-frequently < 1.0
--------------------------------------

This app was actually a part of
`django-frequently <https://github.com/bitmazk/django-frequently>`_. At some
point we had to get rid of django-cms dependencies in that app, so we carved
out all django-cms relevant parts and put them into this cmsplugin app.

If you were using django-frequently<1.0 please make sure that you follow these
instructions very closely:

1. Update to django-frequently<1.0 and run the migrations to make sure that
   your DB is at the latest version of the old frequently app
2. Update the django-frequently to the latest version and install
   cmsplugin-frequently like described above
3. Add ``cmsplugin_frequently`` to your ``INSTALLED_APPS``
4. Run the first migration via ``./manage.py migrate cmsplugin_frequently 0001 --delete-ghost-migrations``
5. Migrate your old plugins to this new app via ``./manage.py migrate_to_frequently_v1``

Step 5 deletes your migrations for django-frequently from
``south_migrationhistory`` because for version 1 we have reset the South
mirations. To get back to the latest migration, do the following::

  ./manage.py migrate frequently 0001 --fake
  ./manage.py migrate frequently
  ./manage.py migrate cmsplugin_frequently


Usage
-----

Just login to the Pages admin and place the plugin whereever you would like to
render a cateogry of the frequently app.

IMPORTANT: Make sure to include the js file in the cms template::

    <script type="text/javascript" src="{{ STATIC_URL }}frequently/js/frequently.js"></script>


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 cmsplugin-frequently
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
