# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(
    name="TanTan",
    version="0.1.0",
    author="Joaquin Rosales",
    author_email="globojorro@gmail.com",
    packages=["tantan"],
    scripts=[],
    url="https://pypi.python.org/pypi/TanTan",
    license="LICENSE.txt",
    description="An open-source application for communicating with \
        Physical-Area-Networks using the ZigBee protocol",
    long_description="""A collection of services, protocols, clients and
        servers based on the Twisted framework.
        """,
    install_requires=[
        "pySerial",
        "pyOpenSSl",
        "Twisted == 13.1.0",
        "autobahn == 0.8.6",
        "paisley",
        "txXBee"
    ],
)
