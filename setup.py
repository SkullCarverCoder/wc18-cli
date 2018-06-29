#!/usr/bin/env python

from setuptools import setup, find_packages
import os, sys

if os.environ.get('USER','') == 'vagrant':
    del os.link

setup(
    name='wc18-cli',
    version='0.0.1.7',
    description='An easy command line interface for the 2018 World Cup',
    author='Juan Hernandez',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stablegit
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'
    ],
    keywords="soccer football worldcup tool cli",
    author_email='juanl182@gmail.com',
    url='https://github.com/SkullCarverCoder/wc18-cli',
    packages=find_packages(),
    include_package_data = True,
    install_requires=[
        "click==6.7",
        "pytz==2018.4",
        "tzlocal==1.5.1",
        "requests==2.18.4",
        "python-dateutil==2.7.3"
    ] + (["colorama==0.3.9"] if "win" in sys.platform else []),
    entry_points={
        'console_scripts': [
            'wc18 = wc18.wc18:main'
        ],
    }
)
