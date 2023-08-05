django-resto (REplicated STOrage) provides file storage backends that can
store files coming into a Django site on several servers in parallel, using
HTTP. ``HybridStorage`` and ``AsyncStorage`` will store the files locally on
the filesystem and remotely, while ``DistributedStorage`` will only store them
remotely.

This works for files uploaded by users through the admin or through custom
Django forms, and also for files created by the application code, provided it
uses the standard `storage API`_.

django-resto is useful for sites deployed in a multi-server environment, in
order to accept uploaded files and have them available on all media servers
for subsequent web requests that could be routed to any machine.

`django-resto`_ is a fork of `django_dust`_ with a strong focus on
consistency, while django_dust is more concerned with availability.

django-resto is released under the BSD license, like Django itself.

.. _storage API: http://docs.djangoproject.com/en/dev/ref/files/storage/
.. _django-resto: https://github.com/aaugustin/django-resto
.. _django_dust: https://github.com/isagalaev/django_dust

