#!/usr/bin/python

""" setup.py for pms.

http://kaveensblog.wordpress.com

"""

try: 
	from setuptools import setup
except ImportError: 
	from distutils.core import setup
setup(
    name="Free-Tele",
    version="0.2.1",
    description="Search, Download Tv episodes via Torrent",
    keywords=["tv", "episodes", "torrent", "search", "movies", "download"],
    author="Kaveen Rodrigo",
    author_email="u.k.k.rodrigo@gmail.com",
    url="http://kaveensblog.wordpress.com",
    install_requires=['wxPython','beautifulsoup4'],
    scripts=['freetele'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: Multimedia",
        "Topic :: Internet :: WWW/HTTP"],
    long_description=open("README").read()
)
