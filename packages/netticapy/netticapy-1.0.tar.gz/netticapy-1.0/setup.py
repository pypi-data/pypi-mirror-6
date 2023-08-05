# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import netticapy

setup(
    name='netticapy',
    version=netticapy.__version__,
    description='A nettica.com API wrapper.',
    long_description="NetticaPy is a python wrapper around Nettica's "
                     "SOAP DNS API.",
    author='Fabian Topfstedt',
    author_email='topfstedt@schneevonmorgen.com',
    url='https://bitbucket.org/fabian/netticapy',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    install_requires=[
        'suds',
    ],
)
