#!/usr/bin/env python

# cat README.rst | sed '{N; N; s/::\n\n\s#!\(.*\)/.. code-block:: \1/g}'
# sed '{s/^\s*#!\(.*\)/.. code-block:: \1/; s/^:://g}'
from distutils.core import setup
import os

try:
    p = os.popen('pandoc -f markdown -t rst README.md | sed \'{s/^\\s*#!\\(.*\\)/.. code-block:: \\1\\n/; s/^:://g}\'')
    long_descr = ''.join(p.readlines())
except:
    long_descr = ''

setup(
    name="dict2colander",
    version="0.2",
    description='Dictionary to Colander schema conversion library',
    author='Peter Facka',
    url='https://bitbucket.org/pfacka/dict2colander',
    author_email='pfacka@binaryparadise.com',
    keywords='schema validation dictionary Colander YAML JSON',
    license='MIT Licence (http://opensource.org/licenses/MIT)',
    long_description=long_descr,
    packages=[
        'dict2colander',
    ],
    requires=[
        'colander(>=1.0)',
    ],
    provides=['dict2colander (0.2)'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: POSIX',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      ],
)
