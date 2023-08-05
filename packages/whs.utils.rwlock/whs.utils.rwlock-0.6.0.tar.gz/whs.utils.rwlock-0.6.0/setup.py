from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

TOP_LEVEL_NAME = "whs"

setup(name=TOP_LEVEL_NAME+'.utils.rwlock',
      version='0.6.0',
      description='This is specific kind of lock, that allows only one operation '
    'at the time (read or write) by any number of callers.',
      long_description='''WHS Ltd provides collection of pure-python modules.

This is implementation of lock, that allows only one kind of operation be
executed at the time (reading or writing). Any number of callers
can acquire reading or writing at once, but if someone tries to acquire writing
while reading is acquired, it will wait, until all readers that acquired lock
release it (and vice versa).

At the moment it works only with threading, but few simple modifications will
result in multiprocessing-enabled implementation.

whs.utils.rwlock is a package, but should be used as a module (all code is in
__init__.py).
''',
      maintainer = "Filip Malczak",
      maintainer_email='filip(dot)malczak(at)gmail(dot)com',
      url='devzone.itadmin.pl',
      namespace_packages=[
          TOP_LEVEL_NAME,
      ],
      packages=[
          TOP_LEVEL_NAME+'.utils.rwlock'
      ],
      py_modules=[
          "ez_setup"
      ],
      license = "BSD license (http://opensource.org/licenses/bsd-license.php); "
      "owner: Web Harvesting Solutions Ltd; "
      "year: 2013",
      platforms =[ "Any"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Utilities"
      ],
     )

