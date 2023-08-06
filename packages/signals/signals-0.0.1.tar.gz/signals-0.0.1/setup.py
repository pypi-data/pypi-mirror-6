#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'

setup(name='signals',
      version=version,
      description="Object notifier and pubsub",
      long_description="",
      classifiers=["Development Status :: 1 - Planning",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: Implementation :: PyPy"],
      keywords="pubsub notify listen emit",
      author='@stevepeak',
      author_email='steve@stevepeak.net',
      url='http://github.com/stevepeak/signals',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['signals'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points=None)
