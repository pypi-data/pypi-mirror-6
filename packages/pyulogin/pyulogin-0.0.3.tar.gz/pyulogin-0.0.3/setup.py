#!/usr/bin/env python
from setuptools import setup, find_packages
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pyulogin',
      url = 'https://github.com/GDAproj/pyulogin',
      version='0.0.3',
      description='Package for work with service ulogin.ru',
      author='Gurov Dmitri',
      author_email='opengurdev@gmail.com',
      classifiers = ['Development Status :: 2 - Pre-Alpha','Environment :: Web Environment','License :: OSI Approved :: MIT License'], 
      license = "MIT",
      keywords = "uLogin",
      packages = find_packages(),
      long_description=read('README.txt'),
      exclude_package_data = {'': ['.gitignore']},	
      include_package_data = True,
     )

