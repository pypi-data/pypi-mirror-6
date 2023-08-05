#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='xml2obj',
      version='0.1',
      description='A simple function to converts XML data into native Python object',
      author='Wai Yip Tung',
      maintainer='Lingchao Xin',
      maintainer_email='douglarek@gmail.com',
      py_modules=['xml2obj'],
      include_package_data=True,
      zip_safe=False,
      classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        ),
)

