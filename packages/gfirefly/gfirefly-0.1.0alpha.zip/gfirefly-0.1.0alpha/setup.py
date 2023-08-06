from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='gfirefly',
      version=version,
      description="Achieve firefly based on gtwisted",
      long_description="""Achieve firefly based on gtwisted""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='gevent gtwisted pb firefly gevent',
      author='lanjinmin',
      author_email='zhuiming.mu@gmail.com',
      url='http://www.9miao.com/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	  scripts = [],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
		  "twisted",
		  "gevent",
		  "gtwisted",
		  "flask",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
