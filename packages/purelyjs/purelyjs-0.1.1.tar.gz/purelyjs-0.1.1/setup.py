from setuptools import find_packages
from setuptools import setup

import purelyjs


setup(
    name='purelyjs',
    version=purelyjs.__version__,
    description='A super simple testing framework for javascript',
    author='Martin Matusiak',
    author_email='numerodix@gmail.com',
    url='https://github.com/numerodix/purelyjs',

    packages=find_packages('.'),
    package_dir = {'': '.'},
    package_data={
        'purelyjs': ['js/*.js'],
    },

    # don't install as zipped egg
    zip_safe=False,

    entry_points={
        "console_scripts": [
            "purelyjs = purelyjs.main:main",
        ]
    },

    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: Apache Software License',
    ],
)
