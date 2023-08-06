from setuptools import setup, find_packages
import sys, os

version = '0.1.3'

setup(name='RPICappReport',
      version=version,
      description="some RPI Capp Report parsing functionality",
      long_description=("retrieve courses taken (and passed)"),
      classifiers=[
        "Topic :: Utilities",
      ],
      packages=['RPICappReport'],
      keywords='RPI Capp Report RPICappReport',
      author='linksapprentice1',
      author_email='linksapprentice1@gmail.com',
      url='http://pythonhosted.org/RPICappReport',
      license= 'MIT',
      include_package_data=True,
      zip_safe=True,
      )
