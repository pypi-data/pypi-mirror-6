TheHerk Resources
=================

TheHerk Resources is a Django application for keeping track of and referencing resources like organizations and people (for now).

Each allows the addition of many contact types with a very straightforward admin interface.

It also includes Django-cms plugins for displaying the data in a few different ways.

Usage
-----

1. Add "resources" and "localflavor" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'localflavor',
            'resources',
        )

2. Run `python manage.py migrate resources`.

   Alternately, you could `syncdb` and `migrate --fake`
