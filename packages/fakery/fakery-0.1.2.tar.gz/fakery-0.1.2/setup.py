import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='fakery',
    version='0.1.2',
    author='Gary Johnson',
    author_email = 'gary@gjtt.com',
    description = 'Trying to make fudge mocks in Python easier.',
    install_requires=['fudge', 'nose'],
    tests_require=['fudge', 'nose'],
    license = 'MIT License',
    py_modules = ['fakery'],
    )
