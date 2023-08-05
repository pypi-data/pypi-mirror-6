# -*- coding: latin-1 -*-

#!/usr/bin/env python

from distutils.core import setup

setup(name='textmodel',
      version='0.2',
      description = \
          'A datatype holding textual data (textmodel) '\
          'and a text widget (wxtextview) as demonstration. '\
          'Textmodel does not depend on a specific gui-toolkit.',
      author='C. Ecker',
      author_email='chrisecker@zoho.com',
      url='https://pypi.python.org/pypi/textmodel/',
      license='See file LICENSE',
      packages=['textmodel', 'wxtextview'],
      #description= 'pure python text data and widget',
      platforms = ['any'],
     )

