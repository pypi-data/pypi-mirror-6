import base62

from setuptools import setup

setup(
    name='base-62',
    version=base62.__version__,
    py_modules=['base62'],
    entry_points={
        'console_scripts': [
            'base62 = base62:main',
        ]
    },
    test_suite = 'nose.collector',
)
