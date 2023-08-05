"""
Funnel
------------

Flask extension for Beaker
"""
from setuptools import setup

setup(name='Funnel',
      version='0.1',
      description='Flask extension for Beaker',
      long_description=__doc__,
      author='longfin',
      author_email='longfin@spoqa.com',
      url='http://github.com/spoqa/funnel',
      py_modules=['flask_funnel'],
      test_suite='test_funnel',
      tests_require=['flask-testing'],
      zip_safe=True,
      install_requires=[
          'Flask>=0.8',
          'Beaker==1.6.3'
      ])
