#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='GauminIpuinWriter',
    version='0.1',
    description='Interactive book editor',
    author='Ales Zabala Alava (Shagi)',
    author_email='shagi@gisa-elkartea.org',
    url='http://lagunak.gisa-elkartea.org/projects/gauminipuin/',
    license='GPLv3+',
    zip_safe=False,
    packages=find_packages(),
    package_data={
        '': ['*.kv', 'imgs/*'],
    },
    install_requires=[
        'GauminIpuin',
    ],
    entry_points={
        'console_scripts': (
            'gauminIpuinwriter = gauminipuinwriter.main:main',
        ),
    },
)
