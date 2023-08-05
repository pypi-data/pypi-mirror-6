#!/usr/bin/env python

"""Install the Dānabox command-line client."""


try:
    from setuptools import setup
    USE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    USE_SETUPTOOLS = False

try:
    LONG_DESCRIPTION = open('README.rst').read()
except IOError:
    LONG_DESCRIPTION = 'Dānabox command-line client'

try:
    APACHE_LICENSE = open('LICENSE').read()
except IOError:
    APACHE_LICENSE = 'See http://www.apache.org/licenses/LICENSE-2.0'

KWARGS = {}
if USE_SETUPTOOLS:
    KWARGS = {
        'install_requires': ['docopt', 'PyYAML', 'requests'],
        'entry_points': {'console_scripts': ['danabox = danabox:main']},
    }
else:
    KWARGS = {'scripts': ['deis']}


# pylint: disable=W0142
setup(name='danabox',
      version='0.0.3',
      license=APACHE_LICENSE,
      description='Command-line Client for Dānabox',
      author='Tom Buckley-Houston',
      author_email='tom@tombh.co.uk',
      url='http://danabox.io',
      keywords=[
          'PaaS', 'cloud', 'heroku',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet',
          'Topic :: System :: Systems Administration',
      ],
      py_modules=['danabox'],
      data_files=[
          ('.', ['README.rst']),
      ],
      long_description=LONG_DESCRIPTION,
      requires=['docopt', 'PyYAML', 'requests'],
      zip_safe=True,
      **KWARGS)
