Welcome to gottwall-backend-redis's documentation!
==================================================

gottwall-backend-redis is a Redis transport for `GottWall metrics aggregation platform <http://github.com/GottWall/GottWall>`_

.. image:: https://secure.travis-ci.org/GottWall/gottwall-backend-redis.png
	   :target: https://secure.travis-ci.org/GottWall/gottwall-backend-redis

INSTALLATION
------------

To use gottwall-backend-redis  use `pip` or `easy_install`:

``pip install gottwall-backend-redis``

or

``easy_install gottwall-backend-redis``


USAGE
-----

To configure GottWall with `gottwall-backend-redis` you need specify backend in GottWall config.

.. sourcecode:: python

   BACKENDS = {
      'gw_backend_redis.RedisBackend': {
        'HOST': "127.0.0.1",
        'PORT': 6379,
        'PASSWORD': None,
        'DB': 2,
        "CHANNEL": "gottwall"},
    }



CONTRIBUTE
----------

We need you help.

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
   There is a Contributor Friendly tag for issues that should be ideal for people who are not very familiar with the codebase yet.
#. Fork `the repository`_ on Github to start making your changes to the **develop** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.

.. _`the repository`: https://github.com/GottWall/gottwall-backend-redis/
