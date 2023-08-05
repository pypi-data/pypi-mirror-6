import os.path as p
from setuptools import setup, find_packages

version = '0.2.1'

ROOT = p.abspath(p.dirname(__file__))
README = open(p.join(ROOT, 'README.rst')).read()

setup(name='django-denormalize',
      version=version,
      description="Converts Django ORM objects into data documents, and keeps them in sync",
      long_description=README,
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
