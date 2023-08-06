=============================
dj-libcloud
=============================

.. image:: https://badge.fury.io/py/dj-libcloud.png
    :target: https://badge.fury.io/py/dj-libcloud

Adds easy python 3 and 2.7 support to Django for management of static assets.

Documentation
-------------

The full documentation is at https://dj-libcloud.readthedocs.org.


Quickstart
------------------------

Libcloud verifies server SSL certificates before it lets you do anything. It will search your system for the CA certificate, and if it doesn't find it then it will blow up. See https://libcloud.readthedocs.org/en/latest/other/ssl-certificate-validation.html

Installing CA certificate bundle on Mac OS X::

    # Assuming you are using homebrew for Mac OS X dependency management.
    $ brew install curl-ca-bundle

Install dj-libcloud::

    $ pip install dj-libcloud

Then use it in a project::

    # settings.py

    STATIC_URL = 'https://my-assets.cdn/static/'
    MEDIA_URL = 'https://my-assets.cdn/media/'
    STATICFILES_STORAGE = 'djlibcloud.storage.LibCloudStorage'
    LIBCLOUD_PROVIDERS = {
        'amazon_s3': {
            'type': 'libcloud.storage.types.Provider.S3',
            'user': os.environ.get('AWS_ACCESS_KEY'),
            'key': os.environ.get('AWS_SECRET_KEY'),
            'bucket': 'my-assets-cdn',  
            'secure': True,
        }
    }

    DEFAULT_LIBCLOUD_PROVIDER = 'amazon_s3'

Features
--------

* Works for uploading media assets using Python 3.3 and Django 1.6.
* In theory supports all the backends that libcloud supports.

FAQ
-----

Because you just had to ask.

Why not use dj-static or whitenoise?
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Those are great libraries, but are not what you want when handling user uploaded media.

Why not just update django-storages?
++++++++++++++++++++++++++++++++++++++++++++++++++++++

`libcloud` is awesome and has a dedicated team devoted to it. We can have it do most of the heavy lifting. On the other hand, converting `django-storages` to work with Python 3 looked like too much work. Sometimes you just have to start anew, right?

How can I contribute?
++++++++++++++++++++++++++++++++++++

Please read http://dj-libcloud.readthedocs.org/en/latest/contributing.html

What about compressors like django-pipeline?
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Working on it. Currently the `PipelineCachedCloudStorage` class breaks the second time you run it. See https://github.com/pydanny/dj-libcloud/issues/7

CREDIT
------

Many thanks to Jannis Leidel (@jezdez) for giving me the code to get this started. He's a Django core developer, the master of Django static asset managment, and overall a great great guy.




History
-------

0.1.2 (2014-04-24)
++++++++++++++++++

* Confirmed to work with Python 2.7
* Remove django-pipeline specific code from storages
* Add cookbook to docs that includes django-pipeline

0.1.1 (2014-04-21)
++++++++++++++++++

* Fixed second-time run problem by just using LibCloudStorage class
* Made django-pipeline optional
* Removed unnecessary files
* Moved TODO to issue tracker

0.1.0 (2014-04-21)
++++++++++++++++++

* First release on PyPI.
* Frustration over lack of easy media asset support for Django and Python 3.

