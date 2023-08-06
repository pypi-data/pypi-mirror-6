#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'

setup(name='debris',
      version=version,
      description="Recycle your objects",
      long_description="""Easy methods to manage objects to reduce stress on
                          retreivals.""",
      classifiers=["Development Status :: 1 - Planning",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: Implementation :: PyPy"],
      keywords="cache tornado",
      author='@stevepeak',
      author_email='steve@stevepeak.net',
      url='http://github.com/stevepeak/debris',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['debris'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points=None)
