#!/usr/bin/env python

try:
    from setuptools import setup
except (ImportError):
    from distribute import setup

setup(name='dse',
      version='4.0.0-RC4',
      description='DSE - Simplified "bulk" insert/update/delete for Django.',
      author='Thomas Weholt',
      author_email='thomas@weholt.org',
      long_description=open('README.md').read(),
      include_package_data=True,
      packages=['dse', ],
      url="https://github.com/weholt/dse",
      requires=['django'],
      classifiers=[
          'Development Status :: 4 - Beta',
          #'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
      ],
)
