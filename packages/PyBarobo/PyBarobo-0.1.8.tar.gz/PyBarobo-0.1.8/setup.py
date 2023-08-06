#!/usr/bin/env python

from distutils.core import setup
import distutils.unixccompiler as unixccompiler
import sys
VERSION = '0.1.8'
DESC = 'Native Python Barobo robotics control library'
AUTHOR = 'David Ko'
AUTHOR_EMAIL = 'david@barobo.com'
MAINTAINER = 'David Ko'
MAINTAINER_EMAIL = 'david@barobo.com'
URL = 'http://www.barobo.com'

# sources and stuff for libsfp library
sources = ['libsfp/src/net_byte_order.c', 'libsfp/src/serial_framing_protocol.c']
objects = ['libsfp/src/net_byte_order.o', 'libsfp/src/serial_framing_protocol.o']
if sys.platform == "win32":
  print('Building for WIN32')
  cc = unixccompiler.UnixCCompiler()
  cc.add_include_dir('libsfp/include')
  cc.compile(sources, extra_preargs=['-fPIC'])
  cc.link_shared_object(objects, 'barobo/lib/libsfp.dll')
  setup(name='PyBarobo',
      version=VERSION,
      description=DESC,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      license='GPL',
      platforms='any',
      packages=['barobo'],
      package_dir={'barobo': 'barobo'},
      package_data={'barobo': ['lib/*.dll']}
      #py_modules=['pybarobo']
      )

else:
  cc = unixccompiler.UnixCCompiler()
  cc.add_include_dir('libsfp/include')
  cc.compile(sources, extra_preargs=['-fPIC'])
  cc.link_shared_object(objects, 'barobo/lib/libsfp.so')

  setup(name='PyBarobo',
      version=VERSION,
      description=DESC,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      license='GPL',
      platforms='any',
      packages=['barobo'],
      package_dir={'barobo': 'barobo'},
      package_data={'barobo': ['lib/libsfp.so']}
      #py_modules=['pybarobo']
      )
