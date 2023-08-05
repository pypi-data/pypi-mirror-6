#!/usr/bin/env python
from distutils.core import setup

setup(
	name="ncdistribute",
	version="1.0",
	description="Distribute python projects as single zip files.",
	author="Nicholas Cole",
	author_email="n@npcole.com",
	url="http://www.npcole.com/",
	packages=['ncdistributerlib'],
    scripts=['ncdistributer.py'],
	license='New BSD License',
	classifiers= [
	    #'Development Status :: 5 - Production/Stable',
	    'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
	    'Environment :: Console',
	    'Operating System :: POSIX',
	    #'Environment :: Console :: Curses',
	    'Intended Audience :: Developers',
	    'License :: OSI Approved :: BSD License',
	    'Topic :: Terminals'
	    ],
	long_description = """
Provides the script ncdistributer.py that will package up a python script together with any non-standard libraries into a zip file
that can be executed on a computer with a python interpreter installed.

It is similar to tools such as pyzzer, but aims to be even more straight-forward to use.

This is currently an alpha release.  Feedback to nicholas.cole@gmail.com is
welcome.
"""
)
