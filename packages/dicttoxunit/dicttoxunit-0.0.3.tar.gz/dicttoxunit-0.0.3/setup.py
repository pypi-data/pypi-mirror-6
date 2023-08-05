#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup

setup(
    name='dicttoxunit',
    version='0.0.3',
    description="Convert dictionary to xunit xml format",
    author='Majid Garmaroudi',
    author_email='majid.sadeghi@gmail.com',
    url='https://github.com/dijam/dicttoxunit',
    license='MIT',
    platforms=['all'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    install_requires=['voluptuous>=0.8.4'],
    py_modules=['dicttoxunit'],
    setup_requires=['nose>=1.0']
)
