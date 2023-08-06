from setuptools import setup

setup(
    name="gridly",
    version="0.4.3",
    packages=['gridly'],
    test_suite='test',
    platforms='any',
    install_requires=[
        'enum34'
    ],

    author="Nathan West",
    description="A Python library for managing fixed-size 2D spaces",
    license="LGPLv3",
    url="https://github.com/Lucretiel/gridly",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment'
    ]
)
