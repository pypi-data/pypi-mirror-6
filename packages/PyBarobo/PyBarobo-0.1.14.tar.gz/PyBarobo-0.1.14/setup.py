#!/usr/bin/env python

from distutils.core import setup
import distutils.unixccompiler as unixccompiler
import sys
import os
VERSION = '0.1.14'
DESC = 'Native Python Barobo robotics control library'
AUTHOR = 'David Ko'
AUTHOR_EMAIL = 'david@barobo.com'
MAINTAINER = 'David Ko'
MAINTAINER_EMAIL = 'david@barobo.com'
URL = 'http://www.barobo.com'

def isPackage( filename ):
    return (
        os.path.isdir(filename) and
        os.path.isfile( os.path.join(filename,'__init__.py'))
    )

def packagesFor( filename, basePackage="" ):
    """Find all packages in filename"""
    set = {}
    for item in os.listdir(filename):
        dir = os.path.join(filename, item)
        if isPackage( dir ):
            if basePackage:
                moduleName = basePackage+'.'+item
            else:
                moduleName = item
            set[ moduleName] = dir
            set.update( packagesFor( dir, moduleName))
    return set

packages = packagesFor( ".", basePackage="barobo" )
packages['barobo'] = './barobo'
packages.pop('barobo.barobo')

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
      packages=packages.keys(),
      package_dir=packages,
      package_data={'barobo': ['lib/libsfp.so']}
      #py_modules=['pybarobo']
      )
