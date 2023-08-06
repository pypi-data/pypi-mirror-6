#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='GauminIpuinReader',
    version='0.1',
    description='Interactive book player',
    author='Ales Zabala Alava (Shagi)',
    author_email='shagi@gisa-elkartea.org',
    url='http://lagunak.gisa-elkartea.org/projects/gauminipuin/',
    packages=find_packages(),
    license='GPLv3+',
    zip_safe=False,
    package_data={
        '': ['*.rst', '*.kv', 'imgs/*'],
    },
    install_requires=[
        'GauminIpuin',
    ],
    entry_points={
        'console_scripts': (
            'gauminipuinreader = gauminipuinreader.main:main',
        ),
    },
)
