from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='django_rungevent',
      version=version,
      description="Django Gevent Run Command",
      long_description="""\
Django Gevent Run Command""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django gevent',
      author='Vibhaj Rajan',
      author_email='vibhaj8@gmail.com',
      url='https://github.com/tr4n2uil/django-rungevent',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
