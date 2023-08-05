
import os

from setuptools import setup, find_packages

os.system('make splay_mod.py')

setup(
    name = "splay_mod",
    version = "1.10",
    packages = find_packages(),
    scripts = ['splay_mod.py'],

    # metadata for upload to PyPI
    author = "Daniel Richard Stromberg",
    author_email = "strombrg@gmail.com",
    description='Pure Python splay tree nodule',
    long_description='''
A pure python splay tree class is provided.  It is
thoroughly unit tested, passes pylint, and is known
to run on CPython 2.x, CPython 3.x, Pypy 2.2 and
Jython 2.7b1.
''',
    license = "Apache v2",
    keywords = "Splay tree, dictionary-like, sorted dictionary, cache",
    url='http://stromberg.dnsalias.org/~strombrg/splay-tree',
    platforms='Cross platform',
    classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 2",
         "Programming Language :: Python :: 3",
         ],
)

