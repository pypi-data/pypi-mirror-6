#!/usr/bin/env python
import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

VERSION = '0.1.0'
PATH = os.path.dirname(os.path.abspath(__file__))
try:
    LONG_DESC = '\n===='+open(os.path.join(PATH, 'README.rst'), 'r').read().split('====', 1)[-1]
except IOError: #happens when using tox
    LONG_DESC = ''

setup(name='django-jsonschema',
      version=VERSION,
      description="django-jsonschema converts Django Forms into JSON Schema compatibile representations",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='django json schema',
      author = 'Jason Kraus',
      author_email = 'zbyte64@gmail.com',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://github.com/zbyte64/django-jsonschema',
      license='New BSD License',
      packages=find_packages(exclude=['tests']),
      test_suite='tests.runtests.runtests',
      tests_require=(
        'pep8',
        'coverage',
        'django',
        'Mock',
        'nose',
        'django-nose',
      ),
      include_package_data = True,
      zip_safe = False,
  )
