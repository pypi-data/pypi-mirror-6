#!/usr/bin/env python
import os
from distutils.core import setup

__author__ = u'Ferran Pegueroles'
__copyright__ = u'Copyright 2013, Ferran Pegueroles'
__credits__ = [u'Ferran Pegueroles']


__license__ = 'BSDD'
__version__ = '0.1.1'
__email__ = 'ferran@pegueroles.com'


long_description = open(os.path.join(os.path.dirname(__file__),
                    'README.rst')).read()


setup(
    name='djgeneric',
    version=__version__,
    url='http://bitbucket.org/ferranp/djgeneric',
    author=__author__,
    author_email=__email__,
    license='GPL',
    packages=['djgeneric', 'djgeneric.templatetags'],
    description='Generic utilities for django',
    long_description=long_description,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
