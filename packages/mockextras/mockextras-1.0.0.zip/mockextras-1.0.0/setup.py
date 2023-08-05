# mockextras.fluent
# Matchers and Stubs for mock.
# Copyright (C) 2012-2014 Andrew Burrows
# E-mail: burrowsa AT gmail DOT com

# mockextras 1.0.0
# https://github.com/ahlmss/mockextras

# Released subject to the BSD License
# Please see https://github.com/ahlmss/mockextras/blob/master/LICENSE.txt

if __name__ == "__main__":
    params = dict(name="mockextras",
        version="1.0.0",
        description="Extensions to the mock library",
        author="Andrew Burrows",
        author_email="burrowsa@gmail.com",
        url="https://github.com/ahlmss/mockextras",
        packages=['mockextras'],
        license="BSD",
        long_description="""The mockextras library is designed to be used with the mock library by Michael Foord 
(http://www.voidspace.org.uk/python/mock/). mockextras adds a number of features that
are found in other mocking libraries namely:

* matchers
* stubs
* a fluent API for the configuration of stubs

The documentation is here: http://mockextras.readthedocs.org/
and the source is here: http://github.com/ahlmss/mockextras""",
        classifiers=["Development Status :: 5 - Production/Stable",
                     "Environment :: Console",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: BSD License",
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3.2",
                     "Programming Language :: Python :: 3.3",
                     "Programming Language :: Python :: Implementation :: CPython",
                     "Programming Language :: Python :: Implementation :: PyPy",
                     "Operating System :: OS Independent",
                     "Topic :: Software Development :: Libraries",
                     "Topic :: Software Development :: Libraries :: Python Modules"])

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup
    else:
        params['install_requires'] = ['mock>=0.8.0']

    setup(**params)
