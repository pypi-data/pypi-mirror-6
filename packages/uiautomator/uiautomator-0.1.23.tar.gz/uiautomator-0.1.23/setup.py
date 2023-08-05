#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uiautomator

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requires = ["urllib3>=1.7.1"]

setup(name='uiautomator',
      version=uiautomator.__version__,
      description='Python Wrapper for Android UiAutomator test tool',
      long_description=uiautomator.__doc__,
      author=uiautomator.__author__,
      author_email='xiaocong@gmail.com',
      url='https://github.com/xiaocong/uiautomator',
      install_requires=requires,
      py_modules=['uiautomator'],
      scripts=['uiautomator.py'],
      setup_requires=['nose>=1.0', 'mock>=1.0.1', 'coverage>=3.6'] + requires,
      license='MIT',
      platforms='any',
      classifiers=(
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Testing',
            )
      )
