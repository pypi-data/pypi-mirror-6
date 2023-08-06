#!/usr/bin/env python

from distutils.core import setup, Extension

wrapper = Extension(
	    '_hom4ps', 
	    ['hom4ps_wrap.cxx'], 
	    libraries=['hom4ps']
	)
setup (
    name='Hom4PSpy',
    version='1.0',
    description='Python binding for Hom4PS-3, a numerical nonlinear system solver',
    author='Tianran Chen',
    author_email='chentia1@msu.edu',
    url='http://www.hom4ps3.org',
    py_modules=['hom4ps', 'hom4pspy'],
    ext_modules=[wrapper],
)
