from setuptools import setup, find_packages

setup(
    name='purelyjs',
    version='0.1',
    description='Testing framework for javascript',
    author='Martin Matusiak',
    author_email='numerodix@gmail.com',

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
)
