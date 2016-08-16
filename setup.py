#!/usr/bin/env python

from distutils.core import setup

setup(name='FooDo',
      version='1.0',
      py_modules=['foodo'],
      description='FooDo - A CLI ToDo App',
      author='David Lavelle',
      author_email='dlavelle7@yahoo.ie',
      url='https://github.com/dlavelle7/foodo',
      scripts=['bin/foodo']
     )
