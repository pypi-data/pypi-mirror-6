import os.path as p
from setuptools import setup, find_packages

version = '0.2.2'

desc = """Django-denormalize allows you to convert a tree of Django ORM objects into one data document. With 'data document' we mean a structure of dicts, lists and other primitive types, that can be serialized to JSON or a Python Pickle.

The resulting document can be used in combination with the Django cache layer to create blazingly fast views that do not hit the database. The data can also be synced to a NoSQL store like MongoDB, for consumption by other frameworks, like Meteor (NodeJS based).

If any data changes in the ORM (even if it's on a some deep many-to-many relationship far away from the root object), django-denormalize will automatically trigger a cache invalidation of the root object's document and/or sync the new document to your preferred NoSQL store.
"""

setup(name='django-denormalize',
      version=version,
      description="Converts Django ORM objects into data documents, and keeps them in sync",
      long_description=desc,
      classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'License :: OSI Approved :: MIT License',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django orm cache mongodb nosql meteor',
      author='Konrad Wojas',
      author_email='konrad@wojas.nl',
      url='https://bitbucket.org/wojas/django-denormalize/',
      license='LICENSE',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'test_project']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Django >= 1.4' # It might work on 1.3 too, but I have not tested this. Django 1.5 works.
      ],
      entry_points="""
      """,
      )
