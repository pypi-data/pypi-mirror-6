muto-server
===========

**muto** is a client/server system for cloud-based image manipulation in
[Django] projects. It uses [easy-thumbnails] for the manipulation part and
[boto] for accessing and storing images on [S3].

This is the server part. The client package is called [muto-client].


Installation
------------

You can install the package from PyPI using pip or easy_install:

```bash
$ pip install muto-server
```

Or you can install from the latest source version:

```bash
$ git clone git://github.com/philippbosch/muto-server.git
$ cd muto-server/
$ python setup.py install
```

Add `mutoserver` to your `INSTALLED_APPS` in **settings.py**:

```python
INSTALLED_APPS = (
    # ...
    'mutoserver',
)
```

You also need a [Redis] instance in place.


Configuration
-------------

There are a few configuration settings you can set in your **settings.py**:

* `MUTO_REDIS_URL` – The URL to a Redis instance (defaults to `redis://:6379`)
* `MUTO_AWS_STORAGE_BUCKET_NAME` - The S3 bucket used to store and retrieve images (falls back to `AWS_STORAGE_BUCKET_NAME` if not defined)
* `MUTO_AWS_ACCESS_KEY_ID` and `MUTO_AWS_SECRET_ACCESS_KEY` – Your S3 credentials used to upload to S3 (fall back to `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` respectively if not defined)


Usage
-----

**muto-server** is basically a management command that runs a worker process
and waits for incoming image transformation requests by watching a queue in
Redis. Start the worker like this:

```bash
$ python manage.py watchqueue
```

That's it.


License
-------

[MIT]



[Django]: http://www.djangoproject.com/
[easy-thumbnails]: https://github.com/SmileyChris/easy_thumbnails
[boto]: https://github.com/boto/boto
[S3]: https://aws.amazon.com/s3/
[muto-client]: https://github.com/philippbosch/muto-client
[Redis]: http://redis.io/
[MIT]: http://philippbosch.mit-license.org/
