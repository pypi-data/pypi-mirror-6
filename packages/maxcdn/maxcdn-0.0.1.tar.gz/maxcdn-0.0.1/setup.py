#!/usr/bin/env python
# -*- coding: utf-8 -*-

options = {
    "name"                  : "maxcdn",
    "version"               : "0.0.1",
    "description"           : "A Python REST Client for MaxCDN REST Web Services",
    "author"                : "Joshua P. Mervine",
    "author_email"          : "joshua@mervine.net",
    "license"               : "MIT",
    "keywords"              : "MAxCDN CDN API REST",
    "packages"              : ['maxcdn'],
    "url"                   : 'http://www.maxcdn.com'
}

# additional setuptools data (python 2.x)
install_requires = [
  "requests",
  "requests_oauthlib",
  "certifi",
  "nose",
  "mock"
]
include_package_data = True

try:
    from setuptools import setup
    options["install_requires"] = install_requires
    options["include_package_data"] = include_package_data
    setup(**options)

except ImportError:
    print("ERROR: setuptools wasn't found, please install it")

    #from distutils.core import setup
    #setup(**options)
    #print("WARNING: setuptools wasn't found, either install")
    #print(" setuptools and rerun setup.py or manually install:")
    #for p in install_requires:
        #print("   - "+p)

