#!/usr/bin/env python3

import setuptools

from periapt import version

setuptools.setup(
    name='periapt',
    version=version.VERSION,
    description='Periapt is a simple apt repository generator.',
    author='Eric Naeseth',
    author_email='eric@thumbtack.com',
    url='https://github.com/thumbtack/periapt',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'periapt = periapt.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Software Distribution',
    ]
)
