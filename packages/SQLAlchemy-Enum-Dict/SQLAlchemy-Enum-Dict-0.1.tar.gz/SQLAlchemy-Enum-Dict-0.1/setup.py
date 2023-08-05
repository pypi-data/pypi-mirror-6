import os
import re
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

with open(os.path.join(here, 'sqlalchemy_enum_dict', '__init__.py')) as f:
    pattern = re.compile(r".*__version__ = '(.*?)'", re.S)
    VERSION = pattern.match(f.read()).group(1)


setup(name='SQLAlchemy-Enum-Dict',
      version=VERSION,
      description="Adds convinient EnumDict column to sqlalchemy",
      long_description=README,
      keywords='sqlalchemy enum',
      author='Vitalii Ponomar',
      author_email='vitalii.ponomar@gmail.com',
      url='http://bitbucket.org/ponomar/sqlalchemy-enum-dict',
      license='BSD',
      zip_safe=False,
      platforms='any',
      packages=find_packages(),
      py_modules=['tests'],
      install_requires=['SQLAlchemy'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
)
