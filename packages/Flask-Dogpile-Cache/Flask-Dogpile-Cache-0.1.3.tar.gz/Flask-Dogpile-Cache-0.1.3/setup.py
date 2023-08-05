"""
Flask-Dogpile-Cache
-----

Easy to Init
````````````

.. code:: python

    # config.py

    DOGPILE_CACHE_URLS = ("127.0.0.1:11211",)
    DOGPILE_CACHE_REGIONS = (
        ('hour', 3600),
        ('day', 3600 * 24),
        ('week', 3600 * 24 * 7),
        ('month', 3600 * 24 * 31),
    )


.. code:: python

    # app.py

    from flask import Flask
    from flask.ext.dogpile_cache import DogpileCache
    import config


    app = Flask(__name__)
    app.config.from_object(config)

    cache = DogpileCache()
    cache.init_app(app)

    # Alternative way: cache = DogpileCache(app)


Easy to Use
```````````

.. code:: python

    @cache.region('hour')
    def cached_func(*args):
        print "First time print", args
        return args

    value = cached_func()

    # Invalidating
    cache.invalidate(cached_func, *args)

    # Refreshing
    cache.refresh(cached_func, *args)

    # Setting custom value
    cache.set(cached_func, value, *args)


Easy to Install
```````````

.. code:: bash

    $ pip install Flask-Dogpile-Cache

Links
`````

* `development version
  <http://bitbucket.org/ponomar/flask-dogpile-cache>`_

"""


import os
import re
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

with open(os.path.join(here, 'flask_dogpile_cache.py')) as main_file:
    pattern = re.compile(r".*__version__ = '(.*?)'", re.S)
    VERSION = pattern.match(main_file.read()).group(1)


setup(name='Flask-Dogpile-Cache',
      version=VERSION,
      description="Adds dogpile.cache support to your Flask application",
      long_description=README,
      keywords='caching flask dogpile',
      author='Vitalii Ponomar',
      author_email='vitalii.ponomar@gmail.com',
      url='http://bitbucket.org/ponomar/flask-dogpile-cache',
      license='BSD',
      zip_safe=False,
      platforms='any',
      packages=find_packages(),
      py_modules=['flask_dogpile_cache'],
      install_requires=['Flask',
                        'dogpile.cache>=0.5.2'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
)
