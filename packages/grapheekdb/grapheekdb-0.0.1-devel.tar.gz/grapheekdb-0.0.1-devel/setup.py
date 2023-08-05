# -*- coding:utf-8 -*-

from setuptools import setup, find_packages
from grapheekdb import __version__

setup(
    name="grapheekdb",
    version=__version__,
    author="Raphaël Braud",
    author_email="grapheekdb@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    url="http://github.com/nidus/grapheekdb",
    license="GPL v3",
    description=("GrapheekDB is a fast and lightweight Graph Database",
                 "with various backends : Kyoto Cabinet/Local memory (more coming soon)."),
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
    ],
    install_requires=[
        "pyzmq",
        "gevent",
    ],
    entry_points="""
    [console_scripts]
    grapheekserve = grapheekdb.server.serve:main
    """
)
