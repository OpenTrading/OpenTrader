#!/usr/bin/env python
"""pytest-bdd package config."""

import codecs
import os
import sys
import glob

from setuptools import setup, find_packages
try:
# http://stackoverflow.com/questions/21698004/python-behave-integration-in-setuptools-setup-py
    from setuptools_behave import behave_test
except ImportError:
    behave_test = None
    
dirname = os.path.dirname(__file__)

long_description = (
    codecs.open(os.path.join(dirname, "README.creole"), encoding="utf-8").read() + "\n"
    )

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["zmq"], "excludes": ["tkinter"]}

setup(
    name="OpenTrader",
    description="OpenTrader",
    long_description=long_description,
    author="Open Trading",
    license="LGPL2 license",
    url="https://www.github.com/OpenTrading/OpenTrader",
    version='1.0',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: LGPL2 License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
    ] + [("Programming Language :: Python :: %s" % x) for x in "2.6 2.7".split()],
    install_requires=[
        "configobj",
        "pandas",
        # we'll make zmq default now
        "zmq",
        ],
    extras_require={'plotting': ["matplotlib"],
                    'pybacktest': ["pybacktest"],
                    'rabbit': ["pyrabbit"],
                    'bdd': ["behave"],
                    # we'll make zmq default now
                    # 'zmq': ["zmq"],
                    'amqp': ["pika"],
                    },
    data_files=[('', ['README.creole']),
                ('OpenTrader', glob.glob('OpenTrader/*.ini')),
                ('OpenTrader/Omlettes', glob.glob('OpenTrader/Omlettes/*.ini'))],

    options = {"build_exe": build_exe_options},
    entry_points={
        "console_scripts": [
            "OTCmd2 = OpenTrader.OTCmd2:iMain",
            "OTBackTest = OpenTrader.OTBackTest:iMain",
            "OTPpnAmgc = OpenTrader.OTPpnAmgc:iMain",
        ]
    },
    tests_require=["behave>=1.2.4"],
    cmdclass=behave_test and {"behave_test": behave_test,} or {},
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
