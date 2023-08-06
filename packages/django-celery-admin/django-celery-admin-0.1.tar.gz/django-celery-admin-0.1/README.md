This app adds the ability to manually run a periodic celery task from the Django Admin.  It requires *Django 1.3+* and
[ask/django-celery](http://github.com/ask/django-celery).

This app was forked from and inspired by [erussell/django-redis-status](http://github.com/erussell/django-redis-status).


Installation
---------

Put ``celery_admin`` in your ``INSTALLED_APPS``.

That's all. Only admin-users with ``superuser`` permission can see these stats.
