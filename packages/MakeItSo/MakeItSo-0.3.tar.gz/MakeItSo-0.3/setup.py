import os
from setuptools import setup

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''

version = '0.3'

setup(name='MakeItSo',
      version=version,
      description='filesystem template interpreter',
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='templates',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/',
      license='MPL',
      packages=['makeitso'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'tempita >= 0.5.1',
          'webob',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      makeitso = makeitso.makeitso:main
      make-python-package = makeitso.python:main
      mkpydir = makeitso.mkpydir:main
      script2package = makeitso.script2package:main

      [makeitso.templates]
      python-package = makeitso.python:PythonPackageTemplate
      python-module = makeitso.python:PythonModuleTemplate
      python-script = makeitso.python:PythonScriptTemplate
      setup.py = makeitso.python:SetupPy
      """,
      )
