#!/usr/bin/env python

from distutils.core import setup

setup(name='pwmscan',
      version='0.0.3-dev',
      description='Scans a DNA sequence against a PWM',
      author='Marcus R. Breese',
      author_email='marcus@breese.com',
      url='http://github.com/mbreese/pwmscan/',
      packages=['pwmscan'],
      scripts=['bin/pwmscan']
     )
