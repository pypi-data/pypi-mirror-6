'''
Created on Mar 21, 2014

@author: akusoka1
'''

from setuptools import setup

readme = open("README.txt").read()

setup(name='MD-ELM',
      version='0.1',
      author='Anton Akusok',
      author_email='akusok.a@gmail.com',
      license='MIT',
      description='Mislabeled samples detection with OP-ELM',
      py_modules=['md_elm'])