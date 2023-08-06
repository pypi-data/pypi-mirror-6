TheHerk Events
==============

TheHerk Events is a event posting tool that consists of a Django-cms plugin for showing upcoming events across calendars and has an apphook for viewing calendars and event details.

Usage
-----

1. Add "events" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'resources',
            'events',
        )

2. Run `python manage.py migrate events`.

   Alternately, you could `syncdb` and `migrate --fake`
