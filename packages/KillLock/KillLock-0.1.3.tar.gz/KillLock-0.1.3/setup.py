#!/usr/bin/python

""" setup.py for KillLock.

https://github.com/KaveenR/KilllLock

"""
import platform
try: 
	from setuptools import setup
except ImportError: 
	from distutils.core import setup
setup(
    name="KillLock",
    version="0.1.3",
    description="This program is written to reset those pesky little Android Apps that restrict fromm doing stuff",
    keywords=["Android", "Lock", "Reset", "ADB"],
    author="KaveenR",
    author_email="u.k.k.rodrigo@gmail.com",
    url="http://geeknirvana.org",
    scripts=['killlock'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities"],
    long_description=open("README.md").read()
)
