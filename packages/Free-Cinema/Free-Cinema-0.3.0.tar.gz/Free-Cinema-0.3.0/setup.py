#!/usr/bin/python

""" setup.py for pms.

http://kaveensblog.wordpress.com

"""
import platform
try: 
	from setuptools import setup
except ImportError: 
	from distutils.core import setup
if (platform.system() == "Linux"):
	my_inc = [('/usr/share/pixmaps/', ['freecinema.png']),('/usr/share/applications/', ['freecinema.desktop'])]
else:
	my_inc =None
setup(
    name="Free-Cinema",
    version="0.3.0",
    description="Search, Download movies via Torrent",
    keywords=["MP3", "music", "audio", "search", "movies", "download"],
    author="nagev",
    author_email="u.k.k.rodrigo@gmail.com",
    url="http://kaveensblog.wordpress.com",
    install_requires=['wxPython','beautifulsoup4'],
    scripts=['freecinema'],
    data_files=my_inc,
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
