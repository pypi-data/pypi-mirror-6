# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
  name='arbetsformedlingen',
  version='0.0.1',
  author='Petter Nyman',
  author_email='petter.nyman@willandskill.se',
  packages=find_packages(),
  install_requires = [
    'requests'
  ],
  url='https://github.com/willandskill/arbetsformedlingen',
  license='BSD licence',
  description='Wrapper for http://api.arbetsformedlingen.se/',
)
